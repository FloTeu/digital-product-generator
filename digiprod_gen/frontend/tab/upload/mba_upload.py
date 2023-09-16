import streamlit as st

from typing import List
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

from digiprod_gen.backend.browser.selenium_fns import wait_until_element_exists, scroll_page, focus_element, scroll_to_top_left
from digiprod_gen.backend.browser.upload import selenium_mba
from digiprod_gen.backend.browser.upload.selenium_mba import open_create_new, select_products_and_marketplaces, \
    select_colors, select_fit_types, insert_listing_text, open_dashboard, change_language_to_en
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
    change_language_to_en(session_state.browser.driver)
    session_state.status.mba_login_successfull = True


def upload_mba_product(session_state) -> List[str]:
    """Uploads product data to mba. If exists a lists of warnings ist returned"""
    from digiprod_gen.backend.browser.upload.selenium_mba import upload_image
    import time
    image_pil_upload_ready = session_state.image_gen_data.image_pil_upload_ready
    driver = session_state.browser.driver
    open_create_new(driver)
    wait_until_element_exists(driver, "//*[contains(@class, 'product-card')]")
    select_products_and_marketplaces(driver,
                                     products=session_state.upload_data.settings.product_categories,
                                     marketplaces=session_state.upload_data.settings.marketplaces)
    if not session_state.upload_data.settings.use_defaults:
        select_colors(driver,
                         colors=session_state.upload_data.settings.colors,
                         product_categories=session_state.upload_data.settings.product_categories,
                         )
        select_fit_types(driver,
                         fit_types=session_state.upload_data.settings.fit_types,
                         product_categories=session_state.upload_data.settings.product_categories,
                         )
    # Listing Upload
    if session_state.upload_data.bullet_1 == None and session_state.upload_data.bullet_2 == None:
        st.error('You not defined your listings yet', icon="🚨")
    else:
        # TODO: how to handle case with Marketplace different to com (language of bullets is german for example but form takes englisch text input)
        insert_listing_text(driver, title=session_state.upload_data.title,
                            brand=session_state.upload_data.brand, bullet_1=session_state.upload_data.bullet_1,
                            bullet_2=session_state.upload_data.bullet_2,
                            description=session_state.upload_data.description)

    # Image Upload
    if session_state.image_gen_data.image_pil_upload_ready == None:
        st.error('You not uploaded/generated an image yet', icon="🚨")
    else:
        image_delete_xpath = "//*[contains(@class, 'sci-delete-forever')]"
        remove_uploaded_image(driver, image_delete_xpath)
        upload_image(session_state.browser, image_pil_upload_ready, session_state.crawling_request.search_term)
        wait_until_element_exists(driver, image_delete_xpath)
        # wait some more time just to be sure, that mba is ready for publishing
        time.sleep(3)

    # extract warnings
    # get sibling of warning span tag
    warnings = [w.find_element(By.XPATH, 'following-sibling::*').text
                for w in driver.find_elements(By.XPATH, "//*[contains(@class, 'sci-warning')]")]
    return warnings

def remove_uploaded_image(driver: WebDriver, xpath: str):
    try:
        delete_image_i_tag = driver.find_element(By.XPATH, xpath)
        # Element must be in focus in order to be clickable
        focus_element(driver, delete_image_i_tag)
        scroll_page(driver, -300)
        scroll_to_top_left(driver)
        delete_image_i_tag.click()

    except (NoSuchElementException, ElementClickInterceptedException) as e:
        print("Exception", str(e))
        pass