import time
import click

import streamlit as st
import streamlit.web.bootstrap as st_bootstrap

from io import TextIOWrapper

from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from digiprod_gen.backend_api.utils.decorators import timeit
from digiprod_gen.backend_api.utils.helper import Timer
from digiprod_gen.backend_api.utils import init_environment, initialise_config
from digiprod_gen.backend.image import conversion
from digiprod_gen.backend.data_classes.session import SessionState
from digiprod_gen.backend.data_classes.config import DigiProdGenConfig
from digiprod_gen.backend.browser.upload.selenium_mba import publish_to_mba
from digiprod_gen.backend_api.browser.selenium_fns import get_full_page_screenshot
from digiprod_gen.frontend.session import read_session, update_mba_request, init_session_state
from digiprod_gen.frontend import sidebar
from digiprod_gen.frontend.tab.image_generation.selected_products import display_mba_selected_products
from digiprod_gen.frontend.tab.image_generation.image_editing import set_image_pil_generated_by_user, \
    display_image_editor
from digiprod_gen.frontend.tab.image_generation.image_generation import display_image_generator, \
    display_image_generation_prompt
from digiprod_gen.frontend.tab.upload.views import (display_listing_selection, display_data_for_upload,
                                                    ListingSelectChange,
                                                    display_image_upload, display_marketplace_selector,
                                                    display_product_category_selector, display_product_color_selector,
                                                    display_product_fit_type_selector)
from digiprod_gen.frontend.tab.upload.mba_upload import upload_mba_product
from digiprod_gen.frontend.tab.crawling.tab_crawling import display_mba_overview_products


@timeit
def display_tab_image_gen_views(session_state: SessionState):
    if session_state.status.detail_pages_crawled:
        display_mba_selected_products(session_state.crawling_data, shirts_per_row=session_state.config.view.cards_per_row)

        if session_state.status.prompts_generated:
            predicted_prompts = session_state.image_gen_data.image_gen_prompts
            st.subheader("Suggested Prompts")
            st.write(predicted_prompts)

            st.subheader("Prepare Image for MBA Upload")
            st.markdown(
                "Please either generate the image directly or use one of the example Prompts to generate an image with Midjourney. \nYou can upload the image afterwards and proceed.")

            display_image_generation_prompt(session_state.image_gen_data)
            display_image_generator(session_state.image_gen_data)
        else:
            st.warning('Please click on 3. Prompt Generation')

    if not session_state.status.prompts_generated:
        # display image generation prompt with empty text field for image editor functionality
        display_image_generation_prompt(session_state.image_gen_data)


    set_image_pil_generated_by_user(session_state.image_gen_data)
    if session_state.image_gen_data.image_pil_generated:
        with Timer("display_image_editor"):
           image_pil_upload_ready = display_image_editor(session_state.image_gen_data, session_state.config.image_gen.background_removal)
        # Update session upload ready image
        if image_pil_upload_ready:
            session_state.image_gen_data.image_pil_upload_ready = image_pil_upload_ready

@timeit
def display_tab_upload_views(session_state: SessionState):
    display_image_upload(session_state.image_gen_data, session_state.status)

    # listing generation
    if not session_state.status.listing_generated:
        st.warning('Please click on 4. Listing Generation')


    if session_state.status.detail_pages_crawled:
        if session_state.status.listing_generated:
            display_listing_selection(session_state.upload_data)

        if session_state.image_gen_data.image_pil_upload_ready:
            display_data_for_upload(session_state.image_gen_data.image_pil_upload_ready,
                                    title=read_session(ListingSelectChange.TITLE.value),
                                    brand=read_session(ListingSelectChange.BRAND.value),
                                    bullet_1=read_session(ListingSelectChange.BULLET_1.value),
                                    bullet_2=read_session(ListingSelectChange.BULLET_2.value))

    mba_upload_settings = session_state.upload_data.settings
    display_marketplace_selector(mba_upload_settings)

    use_defaults = st.checkbox("Use MBA defaults")
    mba_upload_settings.use_defaults = use_defaults
    if not use_defaults:
        display_product_category_selector(mba_upload_settings)
        display_product_color_selector(mba_upload_settings)
        display_product_fit_type_selector(mba_upload_settings)

    #if session_state.status.detail_pages_crawled:
    if not session_state.status.mba_login_successfull:
        st.warning("Please login with your MBA credentials (5. MBA Upload)")
    else:
        #display_mba_account_tier(session_state.browser.driver)
        errors = []
        if st.button("Upload product to MBA"):
            with st.spinner("Upload mba product"):
                try:
                    warnings, errors = upload_mba_product(session_state)
                except NoSuchElementException as e:
                    st.error("Something went wrong during upload")
                    display_full_page_screenshot(session_state.browser.driver)
                    raise e

            for warning in warnings:
                st.warning(f"MBA Warning: {warning}")
            for error in errors:
                st.error(f"MBA Error: {error}")
        if len(errors) == 0 and st.button("Publish to MBA"):
            try:
                publish_to_mba(session_state.browser.driver, searchable=True)
            except Exception as e:
                st.error("Something went wrong during publishing")
                display_full_page_screenshot(session_state.browser.driver)
            time.sleep(1)
            session_state.browser.driver.find_element(By.CLASS_NAME, "btn-close").click()
            st.balloons()


def display_admin_views(session_state: SessionState):
    """Display some options for the admin"""
    if  st.experimental_user.email in st.secrets.admin.emails or st.session_state["mba_email"] in st.secrets.admin.emails:
        st.subheader("Admin View")
        if session_state.browser:
            if st.button("Show Browser Screenshot"):
                display_full_page_screenshot(session_state.browser.driver)
            st.download_button('Download Browser Source', session_state.browser.driver.page_source, file_name="source.html")


def display_full_page_screenshot(driver):
    screenshot_bytes = get_full_page_screenshot(driver)
    screenshot_pil = conversion.bytes2pil(screenshot_bytes)
    st.image(screenshot_pil)


@timeit
def display_views(session_state: SessionState, tab_crawling, tab_ig, tab_upload):
    """Renders views based on session data"""
    with tab_crawling:
        overview_designs_view = session_state.views.get_or_create_overview_designs()
        # before re rendering, empty all existing elements in view
        overview_designs_view.empty()

        with overview_designs_view.container():
            if session_state.status.overview_page_crawled:
                display_mba_overview_products(session_state.crawling_data, session_state.crawling_request, shirts_per_row=session_state.config.view.cards_per_row)

    with tab_ig:
        display_tab_image_gen_views(session_state)

    with tab_upload:
        display_tab_upload_views(session_state)

    display_admin_views(session_state)

@timeit
def display_sidebar(session_state: SessionState, tab_crawling, tab_ig, tab_upload):
    """Renders sidebar elements based on session data"""
    sidebar_element = session_state.views.get_or_create_sidebar()
    # before re rendering, empty all existing views
    sidebar_element.empty()

    with sidebar_element.container():
        sidebar.crawling_mba_overview_input()
        if session_state.status.overview_page_crawled:
            mba_products = session_state.crawling_data.mba_products
            sidebar.crawling_mba_details_input(mba_products, tab_ig)
            mba_products_selected = session_state.crawling_data.get_selected_mba_products()
            if session_state.status.detail_pages_crawled:
                mba_products_selected = session_state.crawling_data.get_selected_mba_products()
            if mba_products_selected and session_state.status.detail_pages_crawled:
                sidebar.prompt_generation_input(tab_ig, mba_products_selected)

        if session_state.status.detail_pages_crawled:
            sidebar.listing_generation_input(tab_upload)

        # MBA Login
        sidebar.mab_login_input(tab_upload)
        try:
            if session_state.browser:
                sidebar.mba_otp_input(session_state)
        except WebDriverException:
            # TODO: Find out why this error is thrown
            pass


def main(config: DigiProdGenConfig):
    init_environment()
    init_session_state(config)

    st.header("MBA Product Generator")
    tab_crawling, tab_ig, tab_upload = st.tabs(["Crawling", "Image Generation", "MBA Upload"])
    session_state: SessionState = st.session_state["session_state"]

    # display views (+ add defaults to session)
    display_sidebar(session_state, tab_crawling, tab_ig, tab_upload)
    display_views(session_state, tab_crawling, tab_ig, tab_upload)

    # init session request
    if session_state.crawling_request == None:
        update_mba_request()


@click.command()
@click.option("-c", "--config", default="config/app-config.yaml", type=click.Path(exists=True))
def start_digiprod_gen(config: TextIOWrapper):
    if st.runtime.exists():
        # The app has been executed with `streamlit run app.py`
        config_obj: DigiProdGenConfig = initialise_config(
            config_file_path=config
        )
        main(config=config_obj)
    else:
        # If the file has been executed with python (`python app.py`), the streamlit functionality
        # won't work. This line reruns the app within the streamlit context, as if it has been
        # executed with `streamlit run app.py`.
        # This is necessary when installing this project from a .whl package, since the executable
        # only gets execute by python and not by streamlit.
        args: list[str] = [config]

        st_bootstrap.run(
            __file__,
            command_line="",
            args=args,
            flag_options={},
        )

if __name__ == "__main__":
    start_digiprod_gen()