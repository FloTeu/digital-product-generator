import streamlit as st
from selenium.webdriver.chrome.webdriver import WebDriver
from digiprod_gen.backend.browser.selenium_fns import init_selenium_driver
from digiprod_gen.backend.browser.upload import selenium_mba
from digiprod_gen.backend.data_classes.session import SessionState
from digiprod_gen.frontend.session import write_session, read_session, set_session_state_if_not_exists
from digiprod_gen.backend.image import conversion
from digiprod_gen.backend.utils import is_debug

def login_to_mba(tab_upload) -> WebDriver:
    set_session_state_if_not_exists()
    session_state: SessionState = read_session("session_state")
    with tab_upload, st.spinner('Setup MBA upload...'):
        # TODO: This might need to be changed as it was copied by browser url directly
        login_post_url = "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=3600&openid.return_to=https%3A%2F%2Fmerch.amazon.com%2Fdashboard&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=amzn_gear_us&openid.mode=checkid_setup&language=en_US&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
        session_state.browser.driver.get(login_post_url)
        selenium_mba.login_mba(session_state.browser.driver, read_session("mba_email"), read_session("mba_password"))
    if "your password is incorrect" in session_state.browser.driver.page_source.lower():
        st.exception(ValueError("Password is incorrect"))
    elif "verification" not in session_state.browser.driver.page_source.lower():
        selenium_mba.wait_until_dashboard_is_ready(session_state.browser.driver)
        session_state.status.mba_login_successfull = True

def display_mba_account_tier(driver: WebDriver):
    tier_element_list = selenium_mba.wait_until_dashboard_is_ready(driver)
    image_pil = conversion.bytes2pil(tier_element_list.screenshot_as_png)
    st.image(image_pil)

def mba_otp_verification(session_state: SessionState, otp_code):
    selenium_mba.authenticate_mba_with_opt_code(session_state.browser.driver, otp_code)
    selenium_mba.wait_until_dashboard_is_ready(session_state.browser.driver)
    session_state.status.mba_login_successfull = True

