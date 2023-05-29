import os
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from digiprod_gen.frontend.session import update_mba_request
from digiprod_gen.backend.data_classes.mba import MBAMarketplaceDomain
from digiprod_gen.backend.data_classes.session import SessionState
from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display
from digiprod_gen.frontend.tab.image_generation.selected_products import crawl_details_update_overview_page
from digiprod_gen.frontend.tab.image_generation.prompt_generation import prompt_generation_refresh_overview
from digiprod_gen.frontend.tab.upload.mba_upload import mba_otp_verification
from digiprod_gen.backend.browser.upload.selenium_mba import login_to_mba
from digiprod_gen.backend.utils import is_debug

def crawling_mba_overview_input(tab_crawling: DeltaGenerator):
    st.sidebar.subheader("1. Crawling MBA Overview")
    st.sidebar.checkbox(label="Speed up Crawling", value=is_debug(), key="speed_up")
    st.sidebar.text_input(value="Unicorn", label="Search Term", on_change=update_mba_request, key="search_term")
    st.sidebar.selectbox("MBA Marketplace",
                                       options=[MBAMarketplaceDomain.COM, MBAMarketplaceDomain.DE], on_change=update_mba_request, key="marketplace")
    st.sidebar.button("Start Crawling", on_click=crawl_mba_overview_and_display, args=(tab_crawling, ))


def crawling_mba_details_input(mba_products, tab_crawling: DeltaGenerator, tab_ig: DeltaGenerator, driver):
    st.sidebar.subheader("2. Crawling MBA Product Pages")
    st.sidebar.multiselect("Select Designs for prompt generation:", [i+1 for i in range(len(mba_products))], key='selected_designs', on_change=crawl_mba_overview_and_display, args=(tab_crawling, ))
    st.sidebar.button("Start Crawling Details", on_click=crawl_details_update_overview_page, args=(tab_ig, tab_crawling, driver), key="button_crawl_detail")


def prompt_generation_input(tab_crawling: DeltaGenerator, tab_ig: DeltaGenerator):
    st.sidebar.subheader("3. Prompt Generation")
    st.sidebar.button("Start Prompt Generation", on_click=prompt_generation_refresh_overview, args=(tab_ig, tab_crawling, ), key="button_prompt_generation")


def mab_login_input(tab_upload: DeltaGenerator):
    st.sidebar.subheader("4. MBA Upload")
    st.sidebar.text_input("MBA Email", value=os.environ.get("mba_user_name", ""), key="mba_email")
    st.sidebar.text_input("MBA Password", type="password", value=os.environ.get("mba_password", ""), key="mba_password")
    st.sidebar.button("Login", on_click=login_to_mba, args=(tab_upload, ), key="button_mba_login")

def mba_otp_input(session_state: SessionState):
    # Only show input if amazon asks for otp
    driver = session_state.browser.driver
    if driver and "verification" in driver.page_source.lower() and "otp" in driver.page_source.lower():
        otp_code = st.sidebar.text_input("OTP")
        st.sidebar.button("Send OTP Token", on_click=mba_otp_verification, args=(session_state, otp_code, ), key="button_send_otp_token")