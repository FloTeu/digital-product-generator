import streamlit as st
from selenium.webdriver.chrome.webdriver import WebDriver
from digiprod_gen.backend.browser.upload import selenium_mba
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

