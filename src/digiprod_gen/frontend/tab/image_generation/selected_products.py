from io import BytesIO
import requests
import time
from bs4 import BeautifulSoup
from streamlit.delta_generator import DeltaGenerator
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException

from digiprod_gen.backend.data_classes import CrawlingMBARequest, MBAProduct


import streamlit as st


from operator import itemgetter
from typing import List
from digiprod_gen.backend.io.io_fns import image_url2image_bytes_io
from digiprod_gen.backend.transform.transform_fns import extend_mba_product
from digiprod_gen.backend.utils import split_list, get_config
from digiprod_gen.backend.crawling.selenium_fns import mba_search_overview_and_change_postcode
from digiprod_gen.constants import MAX_SHIRTS_PER_ROW
from digiprod_gen.frontend.session import reset_selenium_driver
from digiprod_gen.frontend.session import read_session, write_session
from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display


def get_selected_mba_products(mba_products) -> List[MBAProduct]:
    selected_designs = st.session_state['selected_designs']
    # transform human selection to machine index
    selected_designs_i = [i - 1 for i in selected_designs]
    if not selected_designs:
        return []
    if len(selected_designs_i) == 1:
        return [mba_products[selected_designs_i[0]]]
    else:
        return list(itemgetter(*selected_designs_i)(mba_products))


def get_selected_mba_products_by_url(request: CrawlingMBARequest) -> List[MBAProduct]:
    mba_products = read_session([request.get_hash_str(), "mba_products"])
    return get_selected_mba_products(mba_products)


def crawl_mba_details(request):
    # with tab_crawling:
    mba_products = read_session([request.get_hash_str(), "mba_products"])
    headers = request.headers
    driver = read_session("selenium_driver")
    # if driver is not active anymore, restart an klick to overview page
    if not driver.service.is_connectable():
        reset_selenium_driver()
        driver = read_session("selenium_driver")
        config = get_config()
        mba_search_overview_and_change_postcode(request, driver, config.mba_marketplace[request.marketplace].postcode)
        driver.get(request.mba_overview_url)

    mba_products_selected = get_selected_mba_products(mba_products)
    mba_products_selected = []
    for i, mba_product in enumerate(mba_products_selected):
        mba_product_detailed = read_session(mba_product.asin)
        if mba_product_detailed != None:
            # Detailed mba product is already available in session
            mba_products_selected[i] = mba_product_detailed
            continue
        # Else crawl detail information
        mba_product_detailed = mba_product

        time.sleep(0.5)
        try:
            element = driver.find_element(By.XPATH, f"//*[@data-asin='{mba_product.asin}']")

            # Find the title (clickable) element
            title_element = element.find_element(By.XPATH, "//h2//a")
            title_element.click()

            html_str = driver.page_source
            time.sleep(1)
            # Go back to overview page again
            driver.execute_script("window.history.go(-1)")
        except Exception as e:
            #print(e.message)
            st.exception(e)
            continue

            #html_str = driver.page_source
            #str.write(html_str)   

        # headers["referer"] = request.mba_overview_url
        # response_product_url = requests.get(
        #     url=mba_product_detailed.product_url,
        #     headers=headers,
        #     proxies = {
        #         "http": request.proxy,
        #         "https": request.proxy
        #     }
        # )
        # html_str = response_product_url.content

        soup = BeautifulSoup(html_str, 'html.parser')
        if "captcha" in soup.prettify():
            raise ValueError("Got a captcha :(")
        # call by reference change of mba_products
        extend_mba_product(mba_product_detailed, soup, request.marketplace)
        # save data to session
        write_session(mba_product.asin, mba_product_detailed)
        mba_products_selected[i] = mba_product_detailed
        #mba_products[selected_designs_i[i]] = mba_product_detailed
    write_session([request.get_hash_str(), "mba_products"], mba_products)
    return mba_products_selected


def crawl_details_update_overview_page(st_tab_ig: DeltaGenerator, st_tab_crawling: DeltaGenerator):
    request: CrawlingMBARequest = read_session("request")
    # Make sure user sees overview page and recreate it from session
    # crawl_mba_overview_and_display(st_tab_crawling)

    with st_tab_ig, st.spinner('Crawling detail pages...'):
        # crawl new detail pages
        crawl_mba_details(request)
        # refresh overview page
        display_overview_products = read_session([request.get_hash_str(), "display_overview_products"])
        display_overview_products.empty()

    crawl_mba_overview_and_display(st_tab_crawling)
    write_session([request.get_hash_str(), "detail_pages_crawled"], True)


def display_mba_products(st_tab_ig: DeltaGenerator, mba_products_selected: List[MBAProduct]):
    with st_tab_ig:
        st.subheader("Selected MBA Products")
        with st.expander("Collapse selected mba products", expanded=True):
            display_cols = st.columns(MAX_SHIRTS_PER_ROW)
            for j, mba_products_splitted_list in enumerate(split_list(mba_products_selected, MAX_SHIRTS_PER_ROW)):
                for i, mba_product in enumerate(mba_products_splitted_list):
                    image_bytes_io: BytesIO = image_url2image_bytes_io(mba_product.image_url)
                    display_cols[i].image(image_bytes_io)
                    display_cols[i].markdown(f":black[Brand: {mba_product.brand}]")
                    display_cols[i].markdown(f":black[Title: {mba_product.title}]")
                    if mba_product.bullets:
                        for bullet_i, bullet in enumerate(mba_product.bullets):
                            display_cols[i].write(f"Bullets {bullet_i+1}: {bullet}")