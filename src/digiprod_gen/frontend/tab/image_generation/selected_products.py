from io import BytesIO
import requests
from bs4 import BeautifulSoup
from streamlit.delta_generator import DeltaGenerator
from digiprod_gen.backend.data_classes import CrawlingMBARequest, MBAProduct


import streamlit as st


from operator import itemgetter
from typing import List
from digiprod_gen.backend.io.io_fns import image_url2image_bytes_io
from digiprod_gen.backend.transform.transform_fns import extend_mba_product
from digiprod_gen.backend.utils import split_list
from digiprod_gen.constants import MAX_SHIRTS_PER_ROW

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
    mba_products_selected = get_selected_mba_products(mba_products)

    for i, mba_product in enumerate(mba_products_selected):
        mba_product_detailed = read_session(mba_product.asin)
        if mba_product_detailed != None:
            # Detailed mba product is already available in session
            mba_products_selected[i] = mba_product_detailed
            continue
        # Else crawl detail information
        mba_product_detailed = mba_product
        headers["referer"] = request.mba_overview_url
        response_product_url = requests.get(
            url=mba_product_detailed.product_url,
            headers=headers,
            proxies = {
                "http": request.proxy,
                "https": request.proxy
            }
        )
        soup = BeautifulSoup(response_product_url.content, 'html.parser')
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
    crawl_mba_overview_and_display(st_tab_crawling)

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
                    display_cols[i].markdown(f":black[{mba_product.title}]")
                    for bullet_i, bullet in enumerate(mba_product.bullets):
                        display_cols[i].write(f"Bullets {bullet_i+1}: {bullet}")