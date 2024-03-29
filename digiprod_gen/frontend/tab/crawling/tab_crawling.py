import math
from typing import List

import streamlit as st

from digiprod_gen.backend.models.request import CrawlingMBARequest
from digiprod_gen.backend.models.session import SessionState, CrawlingData
from digiprod_gen.backend.models.mba import MBAProduct
from digiprod_gen.backend.utils import get_price_display_str, marketplace2currency, split_list
from digiprod_gen.frontend.session import read_session, update_mba_request
from digiprod_gen.frontend.utils import is_mobile

def crawl_mba_overview_and_display():
    """ Display overview products to frontend.
        If data is not available in session already, the data is crawled.
    """
    session_state: SessionState = read_session("session_state")

    # If not set yet, init session request
    if session_state.crawling_request == None:
        update_mba_request()

    mba_products = session_state.crawling_data.mba_products
    if not mba_products or not session_state.status.overview_page_crawled:
        session_state.crawling_request.postcode = session_state.config.mba.get_marketplace_config(
            session_state.crawling_request.marketplace).postcode
        session_id = session_state.session_id
        response = session_state.backend_caller.post(f"/browser/crawling/mba_overview?session_id={session_id}",
                                                     json=session_state.crawling_request.model_dump())
        #start_browser(session_state)
        # request: CrawlingMBARequest = session_state.crawling_request
        if response.status_code != 200:
            return None
        #crawl_mba_overview2mba_products(session_state)
        mba_products_parsed: List[MBAProduct] = [MBAProduct.parse_obj(mba_p) for mba_p in response.json()]
        # Save to session
        session_state.crawling_data.mba_products = mba_products_parsed
        # Update status
        session_state.status.overview_page_crawled = True



#
# def crawl_mba_overview2mba_products(session_state: SessionState):
#     """ Crawl utils overview page and retry until the server returns a 200 status code.
#         Transforms html to list of MBAProduct objects and stores them in session.
#     """
#     request = session_state.crawling_request
#     driver = session_state.browser.driver
#     config = session_state.config
#
#     mba_products: List[MBAProduct] = []
#
#     st.write("Start crawling products")
#     # If signed in, we provide a postcode in order to show products independently of the signed in user
#     postcode = config.utils.get_marketplace_config(request.marketplace).postcode if session_state.status.mba_login_successfull else None
#     # TODO: Why does this call takes several seconds, even after page loaded already
#     search_overview_and_change_postcode(request, driver, postcode=postcode)
#     st.write("Crawling is done. Start to extract product information")
#
#     html_str = driver.page_source
#
#     # Parse to beautiful soup
#     soup = BeautifulSoup(html_str, 'html.parser')
#     product_tags = soup.find_all("div", {"class": "sg-col-inner"})
#     mba_product_tags = [p for p in product_tags if is_mba_product(p)]
#     st.write(f"{len(mba_product_tags)} products extracted")
#
#     for product_tag in mba_product_tags:
#         # Ignore sponsored products
#         if tag_or_children_have_class(product_tag, "sponsored-brand-label-info-desktop"):
#             continue
#         try:
#             mba_product: MBAProduct = overview_product_tag2mba_product(product_tag, marketplace=request.marketplace)
#         except Exception as e:
#             print("Error during html to mba_product conversion", str(e))
#             continue
#         mba_products.append(mba_product)
#
#     if len(mba_products) == 0 and len(mba_product_tags) > 0:
#         st.error(f"{len(mba_product_tags)} products found. But no product could be extracted")
#         time.sleep(3)
#     else:
#         st.write(f"{len(mba_product_tags)} products found. {len(mba_products)} identified as valid")
#
#     # Save to session
#     session_state.crawling_data.mba_products = mba_products
#     # Update status
#     session_state.status.overview_page_crawled = True
#     return mba_products

def display_mba_overview_products(crawling_data: CrawlingData, request: CrawlingMBARequest, shirts_per_row=4):
    """ Displays already crawled utils overview products to frontend.
    """
    currency_str: str = marketplace2currency(request.marketplace)

    def display_mba_overview_product(mba_product: MBAProduct, number: int, st_element):
        st_element.image(mba_product.image_url)
        color = "black" if mba_product.description is None else "green"
        st_element.markdown(f":{color}[{number}. {mba_product.title}]")
        st_element.write(
            f"Price: {get_price_display_str(request.marketplace, mba_product.price, currency_str)}")

    mba_products: List[MBAProduct] = crawling_data.mba_products
    progress_text = "Crawling in progress. Please wait."
    crawling_progress_bar = st.progress(0, text=progress_text)
    #display_overview_products = st.empty()
    if is_mobile():
        for i, mba_product in enumerate(mba_products):
            crawling_progress_bar.progress(math.ceil(100 / len(mba_products) * i) + 1,
                                           text=progress_text)
            display_mba_overview_product(mba_product, i+1, st)
    else:
        display_cols = st.columns(shirts_per_row)
        for j, mba_products_splitted_list in enumerate(split_list(mba_products, shirts_per_row)):
            for i, mba_product in enumerate(mba_products_splitted_list):
                num_shirt: int = (j * shirts_per_row) + i
                crawling_progress_bar.progress(math.ceil(100 / len(mba_products) * num_shirt) + 1,
                                               text=progress_text)
                display_mba_overview_product(mba_product, num_shirt + 1, display_cols[i])

    crawling_progress_bar.empty()

