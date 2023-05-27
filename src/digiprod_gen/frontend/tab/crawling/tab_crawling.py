
import math
from bs4 import BeautifulSoup
from io import BytesIO
from typing import List

import requests
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from selenium.webdriver.common.by import By

from digiprod_gen.backend.crawling.mba.utils import is_mba_product
from digiprod_gen.backend.crawling.selenium_fns import mba_search_overview_and_change_postcode
from digiprod_gen.backend.transform.transform_fns import overview_product_tag2mba_product
from digiprod_gen.constants import MAX_SHIRTS_PER_ROW
from digiprod_gen.backend.data_classes import CrawlingMBARequest, MBAProduct, MBAMarketplaceDomain
from digiprod_gen.backend.io.io_fns import image_url2image_bytes_io, send_mba_overview_request
from digiprod_gen.backend.utils import get_price_display_str, marketplace2currency, split_list
from digiprod_gen.frontend.session import read_session, update_mba_request, write_session
from digiprod_gen.backend.utils import is_debug, get_config

def crawl_mba_overview_and_display(st_element: DeltaGenerator):
    """ Display overview products to frontend.
        If data is not available in session already, the data is crawled.
    """
    request: CrawlingMBARequest = read_session("request")
    driver = read_session("selenium_driver")
    marketplace = request.marketplace
    with st_element:
        display_start_crawling = st.empty()
        display_start_crawling.write("Start crawling...")
        currency_str = marketplace2currency(marketplace)

        mba_products = read_session([request.get_hash_str(), "mba_products"])
        if not mba_products:
            crawl_mba_overview2mba_products(request, driver)
            mba_products = read_session([request.get_hash_str(), "mba_products"])

        if read_session("speed_up"):
            mba_products = mba_products[0:8]

        display_mba_overview_products(mba_products, currency_str, marketplace, request)
        # Temp button to download html
        st.download_button('Download HTML', driver.page_source, file_name='mba_overview.html', on_click=crawl_mba_overview_and_display, args=(st_element, ), key="download_overview_html")
        display_start_crawling.empty()


def crawl_mba_overview2mba_products(request: CrawlingMBARequest, driver):
    """ Crawl mba overview page and retry until the server returns a 200 status code.
        Transforms html to list of MBAProduct objects and stores them in session.
    """
    # def resend_request():
    #     # retry with new headers
    #     update_mba_request()
    #     request = read_session("request")
    #     response = send_mba_overview_request(request, timeout=2)
    #     if response.status_code != 200:
    #         st.write("Crawling was not successfull")
    #     return response
    
    # # TODO: how to handle error raises?
    # try:
    #     response = send_mba_overview_request(request, timeout=2)
    #     if response.status_code != 200:
    #         response = resend_request()
    # except requests.exceptions.ConnectTimeout:
    #     response = resend_request()
    # html_str = response.content
    config = get_config()
    
    mba_products: List[MBAProduct] = []

    mba_search_overview_and_change_postcode(request, driver, config.mba_marketplace[request.marketplace].postcode)

    html_str = driver.page_source

    # Parse to beautiful soup
    soup = BeautifulSoup(html_str, 'html.parser')
    product_tags = soup.find_all("div", {"class": "sg-col-inner"})
    mba_product_tags = [p for p in product_tags if is_mba_product(p)]
    for product_tag in mba_product_tags:
        mba_product: MBAProduct = overview_product_tag2mba_product(product_tag, marketplace=request.marketplace)
        mba_products.append(mba_product)
    # save to session
    write_session([request.get_hash_str(), "mba_products"], mba_products)


def display_mba_overview_products(mba_products: List[MBAProduct], currency_str: str, marketplace: MBAMarketplaceDomain, request: CrawlingMBARequest):
    """ Displays already crawled mba overview products to frontend.
    """
    progress_text = "Crawling in progress. Please wait."
    crawling_progress_bar = st.progress(0, text=progress_text)
    display_overview_products = st.empty()
    display_cols = display_overview_products.columns(MAX_SHIRTS_PER_ROW)
    for j, mba_products_splitted_list in enumerate(split_list(mba_products, MAX_SHIRTS_PER_ROW)):
        for i, mba_product in enumerate(mba_products_splitted_list):
            crawling_progress_bar.progress(math.ceil(100 / len(mba_products) * ((j * MAX_SHIRTS_PER_ROW) + i)) + 1,
                                           text=progress_text)
            image_bytes_io: BytesIO = image_url2image_bytes_io(mba_product.image_url)
            # image_pil = Image.open(image_bytes_io)
            display_cols[i].image(image_bytes_io)
            color = "black" if not mba_product.bullets else "green"
            display_cols[i].markdown(f":{color}[{(j * MAX_SHIRTS_PER_ROW) + i + 1}. {mba_product.title}]")
            display_cols[i].write(f"Price: {get_price_display_str(marketplace, mba_product.price, currency_str)}")

    crawling_progress_bar.empty()
    write_session([request.get_hash_str(), "display_overview_products"], display_overview_products)

