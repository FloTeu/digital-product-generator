import os
import streamlit as st

from streamlit.delta_generator import DeltaGenerator

from digiprod_gen.frontend.session import update_mba_request
from digiprod_gen.backend.models.mba import MBAMarketplaceDomain
from digiprod_gen.backend.models.session import SessionState, CrawlingData
from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display
from digiprod_gen.frontend.tab.image_generation.selected_products import crawl_details_update_overview_page
from digiprod_gen.frontend.tab.image_generation.prompt_generation import prompt_generation
from digiprod_gen.frontend.tab.upload.listing_generation import listing_generation
from digiprod_gen.frontend.tab.image_generation.image_captioning import extend_mba_products_with_caption
from digiprod_gen.frontend.session import read_session
from digiprod_gen.backend.utils.utils import booleanize

def crawling_mba_overview_input():
    st.subheader("1. Crawling MBA Overview")
    #st.checkbox(label="Speed up Crawling", value=is_debug(), key="speed_up")
    st.text_input(value="Unicorn", label="Search Term", on_change=update_mba_request, key="search_term")
    st.selectbox("MBA Marketplace",
                 options=[MBAMarketplaceDomain.COM, MBAMarketplaceDomain.DE, MBAMarketplaceDomain.FR], #, MBAMarketplaceDomain.ES, MBAMarketplaceDomain.IT, MBAMarketplaceDomain.JP],
                 on_change=update_mba_request,
                 key="marketplace")
    st.button("Start Crawling", on_click=crawl_mba_overview_and_display)

def crawling_mba_details_input(mba_products, tab_ig: DeltaGenerator):
    st.subheader("2. Crawling MBA Product Pages")
    st.multiselect("Select Designs for prompt generation:", [i+1 for i in range(len(mba_products))], key='selected_designs', on_change=crawl_mba_overview_and_display)
    st.button("Start Crawling Details", on_click=crawl_details_update_overview_page, args=(tab_ig, ), key="button_crawl_detail")

def prompt_generation_input(tab_ig: DeltaGenerator):
    session_state: SessionState = st.session_state["session_state"]
    st.subheader("3. Prompt Generation")
    st.button("Run AI Image Captioning", on_click=extend_mba_products_with_caption,
                      args=(session_state.backend_caller, session_state.crawling_data,), key="button_image_captioning")
    st.button("Start Prompt Generation", on_click=prompt_generation, args=(tab_ig, ), key="button_prompt_generation")

def listing_generation_input(tab_ig: DeltaGenerator):
    st.subheader("4. Listing Generation")
    st.button("Start Listing Generation", on_click=listing_generation, args=(tab_ig, ), key="button_listing_generation")


def mab_login_input(tab_upload: DeltaGenerator):
    session_state: SessionState = st.session_state["session_state"]
    def login_to_mba_fn(tab_upload):
        response = session_state.backend_caller.get(
            f"/browser/upload/mba_login?session_id={session_state.session_id}&proxy={session_state.crawling_request.proxy}",
            auth=(read_session("mba_email"), read_session("mba_password")))
        if response.status_code == 409 and "OTP" in response.text:
            session_state.status.mba_login_otp_required = True
        with tab_upload:
            if response.status_code == 401:
                st.exception(ValueError("Password is incorrect"))
            if response.status_code == 409 and "Captcha" in response.text:
                st.exception(ValueError("Captcha is required"))

        if response.status_code == 200 and booleanize(response.text):
            session_state.status.mba_login_successful = True


    st.subheader("5. MBA Upload")
    if session_state.status.mba_login_successful:
        st.write("Log in: :white_check_mark:")
    else:
        st.text_input("MBA Email", value=os.environ.get("mba_user_name", ""), key="mba_email")
        st.text_input("MBA Password", type="password", value=os.environ.get("mba_password", ""), key="mba_password")
        st.button("Login", on_click=login_to_mba_fn, args=(tab_upload, ), key="button_mba_login")

def mba_otp_input():
    def login_to_mba_send_otp_fn(otp_code):
        session_state: SessionState = st.session_state["session_state"]
        response = session_state.backend_caller.get(
            f"/browser/upload/mba_login_otp?otp_code={otp_code}&session_id={session_state.session_id}&proxy={session_state.crawling_request.proxy}",
            )
        if response.status_code == 200 and booleanize(response.text):
            session_state.status.mba_login_otp_required = False
            session_state.status.mba_login_successful = True

    # Display otp input in sidebar
    otp_code = st.text_input("OTP")
    st.button("Send OTP Token", on_click=login_to_mba_send_otp_fn, args=(otp_code, ), key="button_send_otp_token")
