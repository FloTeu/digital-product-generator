
import streamlit as st
import os, sys

from selenium.common.exceptions import WebDriverException
from digiprod_gen.backend.data_classes.mba import CrawlingMBARequest, MBAMarketplaceDomain, MBAProductCategory

from digiprod_gen.backend.utils import is_debug, get_config, init_environment
from digiprod_gen.backend.image import conversion as img_conversion
from digiprod_gen.backend.data_classes.session import SessionState, DigiProdGenStatus
from digiprod_gen.backend.browser.upload.selenium_mba import upload_image, click_on_create_new, insert_listing_text, select_products_and_marketplaces, publish_to_mba
from digiprod_gen.frontend.session import read_session, update_mba_request, write_session
from digiprod_gen.frontend import sidebar
from digiprod_gen.frontend.tab.image_generation.selected_products import display_mba_products
from digiprod_gen.frontend.tab.image_generation.image_editing import get_image_bytes_by_user, display_image_editor
from digiprod_gen.frontend.tab.upload.views import display_listing_selection, display_data_for_upload
from digiprod_gen.frontend.tab.upload.mba_upload import display_mba_account_tier
from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display

init_environment()

def read_request():
    session_state = read_session("session_state")
    if session_state:
        return session_state.crawling_request
    else:
        return CrawlingMBARequest(search_term="", 
                                  marketplace=MBAMarketplaceDomain.COM, 
                                  product_category=MBAProductCategory.SHIRT,
                                  headers=None,
                                  proxy=None, 
                                  mba_overview_url=None)


def display_views(session_state: SessionState | None, tab_crawling, tab_ig, tab_upload):
    if session_state == None:
        return None
    status: DigiProdGenStatus = session_state.status
    with tab_crawling:
        if status.overview_page_crawled:
            crawl_mba_overview_and_display(tab_crawling)

def main():
    st.header("MBA Product Generator")
    tab_crawling, tab_ig, tab_upload = st.tabs(["Crawling", "Image Generation", "MBA Upload"])
    
    sidebar.crawling_mba_overview_input(tab_crawling)
    #request: CrawlingMBARequest = read_request()
    session_state: SessionState | None = read_session("session_state")

    display_views(session_state, tab_crawling, tab_ig, tab_upload)
    
    if session_state and session_state.status.overview_page_crawled:
        mba_products = session_state.crawling_data.mba_products
        #driver = read_session("selenium_driver")
        sidebar.crawling_mba_details_input(mba_products, tab_crawling, tab_ig, None)
        mba_products_selected = session_state.crawling_data.get_selected_mba_products(read_session("selected_designs"))
        if mba_products_selected and session_state.status.detail_pages_crawled:
            sidebar.prompt_generation_input(tab_ig)
            predicted_prompts = session_state.image_gen_data.image_gen_prompts
            display_mba_products(tab_ig, mba_products_selected)
            if session_state.status.detail_pages_crawled:
                with tab_ig:
                    if session_state.status.prompts_generated:
                        st.subheader("Suggested Prompts")
                        st.write(predicted_prompts)
                    else:
                        st.warning('Please click on 3. Prompt Generation')
                    image_bytes: bytes | None = get_image_bytes_by_user()
                    if image_bytes:
                        image_pil = img_conversion.bytes2pil(image_bytes)
                        image_pil_upload_ready = display_image_editor(image_pil, session_image_gen_data=session_state.image_gen_data, background_removal_buffer=0)
                        if image_pil_upload_ready:
                            session_state.image_gen_data.image_pil_upload_ready = image_pil_upload_ready

    # TODO Clean up
    with tab_upload:
        if session_state:
            image_pil_upload_ready = session_state.image_gen_data.image_pil_upload_ready
            # User can either choose newly created image or choose a existing one
            if not image_pil_upload_ready:
                image = st.file_uploader("Image:", type=["png", "jpg", "jpeg"], key="image_upload_tab")
                if image:
                    image_pil_upload_ready = img_conversion.bytes2pil(image.getvalue())
                    session_state.image_gen_data.image_pil_upload_ready = image_pil_upload_ready

            # listing generation
            if not session_state.status.listing_generated:
                st.warning('Please click on 4. Listing Generation')
            if session_state.status.detail_pages_crawled:
                sidebar.listing_generation_input(tab_upload)
                predicted_bullets = session_state.upload_data.predicted_bullets
                predicted_titles = session_state.upload_data.predicted_titles
                predicted_brands = session_state.upload_data.predicted_brands

        # MBA Login
        sidebar.mab_login_input(tab_upload)
        try:
            if session_state:
                sidebar.mba_otp_input(session_state)
        except WebDriverException:
            # TODO: Find out why this error is thrown
            pass

        if session_state and session_state.status.detail_pages_crawled:
            if predicted_bullets and predicted_brands and predicted_titles:
                display_listing_selection(predicted_titles, predicted_brands, predicted_bullets, tab_crawling)

            if image_pil_upload_ready:
                predicted_description = f'{read_session("mba_upload_title")} by "{read_session("mba_upload_brand")}". {read_session("mba_upload_bullet_1")} {read_session("mba_upload_bullet_2")}'
                display_data_for_upload(image_pil_upload_ready, title=read_session("mba_upload_title"), brand=read_session("mba_upload_brand"), bullet_1=read_session("mba_upload_bullet_1"), bullet_2=read_session("mba_upload_bullet_2"), description=predicted_description)
            if not session_state.status.mba_login_successfull:
                st.warning("Please login with your MBA credentials")
            else:
                display_mba_account_tier(session_state.browser.driver)
                if st.button("Upload product to MBA"):
                    upload_mba_product(session_state, predicted_description, tab_upload)


def upload_mba_product(session_state, predicted_description, tab_upload):
    from digiprod_gen.backend.browser.upload.selenium_mba import login_to_mba
    import time
    login_to_mba(tab_upload)
    image_pil_upload_ready = session_state.image_gen_data.image_pil_upload_ready
    click_on_create_new(session_state.browser.driver)
    time.sleep(1)
    select_products_and_marketplaces(session_state.browser.driver,
                                     products=[session_state.crawling_request.product_category],
                                     marketplaces=[session_state.crawling_request.marketplace])
    upload_image(session_state.browser.driver, image_pil_upload_ready)
    if read_session("mba_upload_bullet_1") == None and read_session("mba_upload_bullet_2") == None:
        st.error('You not defined your listings yet', icon="🚨")
    else:
        # TODO: how to handle case with Marketplace different to com (language of bullets is german for example but form takes englisch text input)
        insert_listing_text(session_state.browser.driver, title=read_session("mba_upload_title"),
                            brand=read_session("mba_upload_brand"), bullet_1=read_session("mba_upload_bullet_1"),
                            bullet_2=read_session("mba_upload_bullet_2"), description=predicted_description)
        # publish_to_mba(searchable=not is_debug())


if __name__ == "__main__":
    main()



