import streamlit as st
from selenium.webdriver.chrome.webdriver import WebDriver

from digiprod_gen.backend.browser.selenium_fns import wait_until_element_exists
from digiprod_gen.backend.browser.upload import selenium_mba
from digiprod_gen.backend.browser.upload.selenium_mba import click_on_create_new, select_products_and_marketplaces, \
    select_colors, select_fit_types, insert_listing_text
from digiprod_gen.backend.data_classes.session import SessionState
from digiprod_gen.backend.image import conversion


def display_mba_account_tier(driver: WebDriver):
    tier_element_list = selenium_mba.wait_until_dashboard_is_ready(driver)
    if tier_element_list:
        image_pil = conversion.bytes2pil(tier_element_list.screenshot_as_png)
        st.image(image_pil)

def mba_otp_verification(session_state: SessionState, otp_code):
    selenium_mba.authenticate_mba_with_opt_code(session_state.browser.driver, otp_code)
    selenium_mba.wait_until_dashboard_is_ready(session_state.browser.driver)
    session_state.status.mba_login_successfull = True


def upload_mba_product(session_state):
    from digiprod_gen.backend.browser.upload.selenium_mba import upload_image
    import time
    image_pil_upload_ready = session_state.image_gen_data.image_pil_upload_ready
    click_on_create_new(session_state.browser.driver)
    wait_until_element_exists(session_state.browser.driver, "//*[contains(@class, 'product-card')]")
    select_products_and_marketplaces(session_state.browser.driver,
                                     products=session_state.upload_data.settings.product_categories,
                                     marketplaces=session_state.upload_data.settings.marketplaces)
    if not session_state.upload_data.settings.use_defaults:
        select_colors(session_state.browser.driver,
                         colors=session_state.upload_data.settings.colors,
                         product_categories=session_state.upload_data.settings.product_categories,
                         )
        select_fit_types(session_state.browser.driver,
                         fit_types=session_state.upload_data.settings.fit_types,
                         product_categories=session_state.upload_data.settings.product_categories,
                         )
    if session_state.image_gen_data.image_pil_upload_ready == None:
        st.error('You not uploaded/generated an image yet', icon="🚨")
    else:
        upload_image(session_state.browser.driver, image_pil_upload_ready)
    if session_state.upload_data.bullet_1 == None and session_state.upload_data.bullet_2 == None:
        st.error('You not defined your listings yet', icon="🚨")
    else:
        # TODO: how to handle case with Marketplace different to com (language of bullets is german for example but form takes englisch text input)
        insert_listing_text(session_state.browser.driver, title=session_state.upload_data.title,
                            brand=session_state.upload_data.brand, bullet_1=session_state.upload_data.bullet_1,
                            bullet_2=session_state.upload_data.bullet_2,
                            description=session_state.upload_data.description)
