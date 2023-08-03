import streamlit as st
import os, sys

from selenium.common.exceptions import WebDriverException
from digiprod_gen.backend.data_classes.mba import CrawlingMBARequest, MBAMarketplaceDomain, MBAProductCategory

from digiprod_gen.backend.utils import is_debug, get_config, init_environment
from digiprod_gen.backend.image import conversion as img_conversion
from digiprod_gen.backend.image.caption import extend_mba_products_with_caption
from digiprod_gen.backend.data_classes.session import SessionState, DigiProdGenStatus
from digiprod_gen.backend.browser.upload.selenium_mba import click_on_create_new, insert_listing_text, \
    select_products_and_marketplaces, publish_to_mba
from digiprod_gen.frontend.session import read_session, update_mba_request, write_session, \
    set_session_state_if_not_exists, init_session_state
from digiprod_gen.frontend import sidebar
from digiprod_gen.frontend.tab.image_generation.selected_products import display_mba_products
from digiprod_gen.frontend.tab.image_generation.image_editing import set_image_pil_generated_by_user, \
    display_image_editor
from digiprod_gen.frontend.tab.image_generation.image_generation import display_image_generator, \
    display_image_generation_prompt
from digiprod_gen.frontend.tab.upload.views import (display_listing_selection, display_data_for_upload,
                                                    ListingSelectChange, display_upload_settings_editor)
from digiprod_gen.frontend.tab.upload.mba_upload import display_mba_account_tier
from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display

init_environment()
init_session_state()


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
    # request: CrawlingMBARequest = read_request()
    session_state: SessionState | None = read_session("session_state")
    # TODO: This is only a temp solution
    if not session_state:
        st.button("Initialize session", on_click=set_session_state_if_not_exists)

    display_views(session_state, tab_crawling, tab_ig, tab_upload)

    if session_state and session_state.status.overview_page_crawled:
        mba_products = session_state.crawling_data.mba_products
        # driver = read_session("selenium_driver")
        sidebar.crawling_mba_details_input(mba_products, tab_crawling, tab_ig)
        if session_state.status.detail_pages_crawled:
            mba_products_selected = session_state.crawling_data.get_selected_mba_products()
            st.sidebar.button("Run AI Image Captioning", on_click=extend_mba_products_with_caption,
                              args=(mba_products_selected,), key="button_image_captioning")
        mba_products_selected = session_state.crawling_data.get_selected_mba_products()
        if mba_products_selected and session_state.status.detail_pages_crawled:
            sidebar.prompt_generation_input(tab_ig)
            predicted_prompts = session_state.image_gen_data.image_gen_prompts
            display_mba_products(tab_ig, mba_products_selected)
            if session_state.status.detail_pages_crawled:
                with tab_ig:
                    if session_state.status.prompts_generated:
                        st.subheader("Suggested Prompts")
                        st.write(predicted_prompts)

                        st.subheader("Prepare Image for MBA Upload")
                        st.markdown(
                            "Please either generate the image directly or use one of the example Prompts to generate an image with Midjourney. \nYou can upload the image afterwards and proceed.")
                        display_image_generation_prompt(session_state.image_gen_data)
                        display_image_generator(session_state.image_gen_data)
                    else:
                        st.warning('Please click on 3. Prompt Generation')
    if session_state:
        with tab_ig:
            if not session_state.status.prompts_generated:
                display_image_generation_prompt(session_state.image_gen_data)
            set_image_pil_generated_by_user(session_image_gen_data=session_state.image_gen_data)
            if session_state.image_gen_data.image_pil_generated:
                image_pil_upload_ready = display_image_editor(session_state.image_gen_data, background_removal_buffer=0)
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

            mba_upload_settings = session_state.upload_data.settings
            display_upload_settings_editor(mba_upload_settings)

        # MBA Login
        sidebar.mab_login_input(tab_upload)
        try:
            if session_state.browser:
                sidebar.mba_otp_input(session_state)
        except WebDriverException:
            # TODO: Find out why this error is thrown
            pass

        if session_state and session_state.status.detail_pages_crawled:
            display_listing_selection(session_state.upload_data)

            if image_pil_upload_ready:
                display_data_for_upload(image_pil_upload_ready, title=read_session(ListingSelectChange.TITLE.value),
                                        brand=read_session(ListingSelectChange.BRAND.value),
                                        bullet_1=read_session(ListingSelectChange.BULLET_1.value),
                                        bullet_2=read_session(ListingSelectChange.BULLET_2.value))
            if not session_state.status.mba_login_successfull:
                st.warning("Please login with your MBA credentials")
            else:
                display_mba_account_tier(session_state.browser.driver)
                if st.button("Upload product to MBA"):
                    upload_mba_product(session_state, tab_upload)


def upload_mba_product(session_state, tab_upload):
    from digiprod_gen.backend.browser.upload.selenium_mba import login_to_mba
    from digiprod_gen.backend.browser.upload.selenium_mba import upload_image
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
        insert_listing_text(session_state.browser.driver, title=session_state.upload_data.title,
                            brand=session_state.upload_data.brand, bullet_1=session_state.upload_data.bullet_1,
                            bullet_2=session_state.upload_data.bullet_2,
                            description=session_state.upload_data.description)
        # publish_to_mba(searchable=not is_debug())


if __name__ == "__main__":
    main()
