import time

import math
from bs4 import BeautifulSoup
from io import BytesIO
from typing import List

import requests
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from selenium.webdriver.common.by import By

from digiprod_gen.backend.browser.crawling.mba.utils import is_mba_product
from digiprod_gen.backend.browser.crawling.selenium_mba import search_overview_and_change_postcode
from digiprod_gen.backend.data_classes.mba import CrawlingMBARequest, MBAMarketplaceDomain
from digiprod_gen.backend.data_classes.session import SessionState, CrawlingData
from digiprod_gen.backend.transform.transform_fns import overview_product_tag2mba_product
from digiprod_gen.backend.data_classes.mba import MBAProduct
from digiprod_gen.backend.browser.crawling.bs_fns import tag_or_children_have_class
from digiprod_gen.backend.io.io_fns import image_url2image_bytes_io, send_mba_overview_request
from digiprod_gen.backend.utils import get_price_display_str, marketplace2currency, split_list
from digiprod_gen.frontend.session import read_session, start_browser, update_mba_request

def crawl_mba_overview_and_display():
    """ Display overview products to frontend.
        If data is not available in session already, the data is crawled.
    """
    session_state: SessionState = read_session("session_state")

    # If not set yet, init session request
    if session_state.crawling_request == None:
        update_mba_request()
    start_browser(session_state)
    # request: CrawlingMBARequest = session_state.crawling_request
    overview_designs_view = session_state.views.overview_designs
    with overview_designs_view:

        mba_products = session_state.crawling_data.mba_products
        if not mba_products or not session_state.status.overview_page_crawled:
            crawl_mba_overview2mba_products(session_state)

        #display_mba_overview_products(session_state.crawling_data, request, shirts_per_row=session_state.config.view.cards_per_row)
        # # Temp button to download html
        # st.download_button('Download HTML', driver.page_source, file_name='mba_overview.html', on_click=crawl_mba_overview_and_display, args=(st_element, ), key="download_overview_html")
        # display_start_crawling.empty()


def crawl_mba_overview2mba_products(session_state: SessionState):
    """ Crawl mba overview page and retry until the server returns a 200 status code.
        Transforms html to list of MBAProduct objects and stores them in session.
    """
    request = session_state.crawling_request
    driver = session_state.browser.driver
    config = session_state.config
    
    mba_products: List[MBAProduct] = []

    st.write("Start crawling products")
    # If signed in, we provide a postcode in order to show products independently of the signed in user
    postcode = config.mba.get_marketplace_config(request.marketplace).postcode if session_state.status.mba_login_successfull else None
    # TODO: Why does this call takes several seconds, even after page loaded already
    search_overview_and_change_postcode(request, driver, postcode=postcode)
    st.write("Crawling is done. Start to extract product information")

    html_str = driver.page_source

    # Parse to beautiful soup
    soup = BeautifulSoup(html_str, 'html.parser')
    product_tags = soup.find_all("div", {"class": "sg-col-inner"})
    mba_product_tags = [p for p in product_tags if is_mba_product(p)]
    st.write(f"{len(mba_product_tags)} products extracted")

    for product_tag in mba_product_tags:
        # Ignore sponsored products
        if tag_or_children_have_class(product_tag, "sponsored-brand-label-info-desktop"):
            continue
        try:
            mba_product: MBAProduct = overview_product_tag2mba_product(product_tag, marketplace=request.marketplace)
        except Exception as e:
            print("Error during html to mba_product conversion", str(e))
            continue
        mba_products.append(mba_product)

    if len(mba_products) == 0 and len(mba_product_tags) > 0:
        st.error(f"{len(mba_product_tags)} products found. But no product could be extracted")
        time.sleep(3)
    else:
        st.write(f"{len(mba_product_tags)} products found. {len(mba_products)} identified as valid")

    # Save to session
    session_state.crawling_data.mba_products = mba_products
    # Update status
    session_state.status.overview_page_crawled = True
    return mba_products

def display_mba_overview_products(crawling_data: CrawlingData, request: CrawlingMBARequest, shirts_per_row=4):
    """ Displays already crawled mba overview products to frontend.
    """
    mba_products: List[MBAProduct] = crawling_data.mba_products
    currency_str: str = marketplace2currency(request.marketplace)
    progress_text = "Crawling in progress. Please wait."
    crawling_progress_bar = st.progress(0, text=progress_text)
    #display_overview_products = st.empty()
    display_cols = st.columns(shirts_per_row)
    for j, mba_products_splitted_list in enumerate(split_list(mba_products, shirts_per_row)):
        for i, mba_product in enumerate(mba_products_splitted_list):
            num_shirt: int = (j * shirts_per_row) + i
            crawling_progress_bar.progress(math.ceil(100 / len(mba_products) * num_shirt) + 1,
                                           text=progress_text)
            #image_bytes_io: BytesIO = image_url2image_bytes_io(mba_product.image_url)
            # image_pil = Image.open(image_bytes_io)
            display_cols[i].image(mba_product.image_url)
            color = "black" if not mba_product.bullets else "green"
            display_cols[i].markdown(f":{color}[{num_shirt + 1}. {mba_product.title}]")
            display_cols[i].write(f"Price: {get_price_display_str(request.marketplace, mba_product.price, currency_str)}")

    crawling_progress_bar.empty()

