import os
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from digiprod_gen.frontend.session import update_mba_request
from digiprod_gen.backend.data_classes.mba import MBAMarketplaceDomain
from digiprod_gen.backend.data_classes.session import SessionState
from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display
from digiprod_gen.frontend.tab.image_generation.selected_products import crawl_details_update_overview_page
from digiprod_gen.frontend.tab.image_generation.prompt_generation import prompt_generation
from digiprod_gen.frontend.tab.upload.listing_generation import listing_generation
from digiprod_gen.frontend.tab.upload.mba_upload import mba_otp_verification
from digiprod_gen.backend.browser.upload.selenium_mba import login_to_mba
from digiprod_gen.backend.utils import is_debug

def crawling_mba_overview_input():
    st.subheader("1. Crawling MBA Overview")
    #st.checkbox(label="Speed up Crawling", value=is_debug(), key="speed_up")
    st.text_input(value="Unicorn", label="Search Term", on_change=update_mba_request, key="search_term")
    st.selectbox("MBA Marketplace",
                 options=[MBAMarketplaceDomain.COM, MBAMarketplaceDomain.DE],#, MBAMarketplaceDomain.FR, MBAMarketplaceDomain.ES, MBAMarketplaceDomain.IT, MBAMarketplaceDomain.JP],
                 on_change=update_mba_request,
                 key="marketplace")
    st.button("Start Crawling", on_click=crawl_mba_overview_and_display)

def crawling_mba_details_input(mba_products, tab_ig: DeltaGenerator):
    st.subheader("2. Crawling MBA Product Pages")
    st.multiselect("Select Designs for prompt generation:", [i+1 for i in range(len(mba_products))], key='selected_designs', on_change=crawl_mba_overview_and_display)
    st.button("Start Crawling Details", on_click=crawl_details_update_overview_page, args=(tab_ig, ), key="button_crawl_detail")

def prompt_generation_input(tab_ig: DeltaGenerator):
    st.subheader("3. Prompt Generation")
    st.button("Start Prompt Generation", on_click=prompt_generation, args=(tab_ig, ), key="button_prompt_generation")

def listing_generation_input(tab_ig: DeltaGenerator):
    st.subheader("4. Listing Generation")
    st.button("Start Listing Generation", on_click=listing_generation, args=(tab_ig, ), key="button_listing_generation")


def mab_login_input(tab_upload: DeltaGenerator):
    st.subheader("5. MBA Upload")
    st.text_input("MBA Email", value=os.environ.get("mba_user_name", ""), key="mba_email")
    st.text_input("MBA Password", type="password", value=os.environ.get("mba_password", ""), key="mba_password")
    st.button("Login", on_click=login_to_mba, args=(tab_upload, ), key="button_mba_login")

def mba_otp_input(session_state: SessionState):
    # Only show input if amazon asks for otp
    driver = session_state.browser.driver
    if driver and "verification" in driver.page_source.lower() and "otp" in driver.page_source.lower():
        otp_code = st.text_input("OTP")
        st.button("Send OTP Token", on_click=mba_otp_verification, args=(session_state, otp_code, ), key="button_send_otp_token")