from io import BytesIO
from streamlit.delta_generator import DeltaGenerator

import streamlit as st

from digiprod_gen.backend.data_classes.session import CrawlingData, SessionState
from digiprod_gen.backend.io.io_fns import image_url2image_bytes_io
from digiprod_gen.backend_api.utils import split_list
from digiprod_gen.backend_api.models.mba import MBAProduct
from digiprod_gen.frontend.session import read_session



def crawl_details_update_overview_page(st_tab_ig: DeltaGenerator):
    session_state: SessionState = read_session("session_state")
    session_state.crawling_data.selected_designs = read_session("selected_designs")

    with st_tab_ig, st.spinner('Crawling detail pages...'):
        mba_products_selected_human = session_state.crawling_data.selected_designs
        for i in mba_products_selected_human:
            # i is a human readable number -> decrement to get index
            mba_products_selected_index = i - 1
            mba_product = session_state.crawling_data.mba_products[mba_products_selected_index]
            # Detailed utils product is already available in session
            if mba_product.bullets != None and mba_product.bullets != []:
                continue
            session_id = session_state.session_id
            response = session_state.backend_caller.post(f"/browser/crawling/mba_product?session_id={session_id}&proxy={session_state.crawling_request.proxy}",
                                                             json=mba_product.dict())
            if response.status_code != 200:
                return None
            session_state.crawling_data.mba_products[mba_products_selected_index] = MBAProduct.parse_obj(response.json())

        # crawl new detail pages
        #crawl_mba_details(session_state)

    session_state.status.detail_pages_crawled = True


def display_mba_selected_products(crawling_data: CrawlingData, shirts_per_row=4):
    mba_products_selected = crawling_data.get_selected_mba_products()
    st.subheader("Selected MBA Products")
    with st.expander("Collapse selected utils products", expanded=True):
        display_cols = st.columns(shirts_per_row)
        for j, mba_products_splitted_list in enumerate(split_list(mba_products_selected, shirts_per_row)):
            for i, mba_product in enumerate(mba_products_splitted_list):
                image_bytes_io: BytesIO = image_url2image_bytes_io(mba_product.image_url)
                display_cols[i].image(image_bytes_io)
                display_cols[i].markdown(f":black[Brand: {mba_product.brand}]")
                display_cols[i].markdown(f":black[Title: {mba_product.title}]")
                if mba_product.bullets:
                    for bullet_i, bullet in enumerate(mba_product.bullets):
                        display_cols[i].write(f"Bullets {bullet_i+1}: {bullet}")
                if mba_product.image_text_caption:
                    display_cols[i].markdown(f":black[Text Caption: {mba_product.image_text_caption}]")
                if mba_product.image_prompt:
                    display_cols[i].markdown(f":black[Image Prompt: {mba_product.image_prompt}]")