import streamlit as st

from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display
from digiprod_gen.backend.data_classes.session import MBAUploadData, SessionState
from collections import deque


def display_listing_selection(predicted_titles, predicted_brands, predicted_bullets, tab_crawling):
    st.subheader("Suggested Product Listing")
    st.selectbox("Suggested Titles:", predicted_titles, on_change=crawl_mba_overview_and_display, args=(tab_crawling, ), key="mba_upload_title")
    
    st.selectbox("Suggested Brands:", predicted_brands, on_change=crawl_mba_overview_and_display, args=(tab_crawling, ), key="mba_upload_brand")

    st.selectbox("Suggested Bullet 1:", predicted_bullets, on_change=crawl_mba_overview_and_display, args=(tab_crawling, ), key="mba_upload_bullet_1")
    # put first element to end of list
    predicted_bullets_shifted = deque(predicted_bullets)
    predicted_bullets_shifted.rotate(-1)
    st.selectbox("Suggested Bullet 2:", predicted_bullets_shifted, on_change=crawl_mba_overview_and_display, args=(tab_crawling, ), key="mba_upload_bullet_2")

def display_data_for_upload(image_pil, title, brand, bullet_1, bullet_2, description=None):
    st.subheader("Upload Overview")
    col1, col2 = st.columns(2)
    col2_1, col2_2 = col2.columns(2)
    col1.image(image_pil)

    session_state: SessionState = st.session_state["session_state"]
    mba_upload_data: MBAUploadData = session_state.upload_data

    # Column 1
    col2_1.text_area("**Title**", value=title, on_change=update_session_upload_listing, args=(mba_upload_data, ), key="mba_upload_listing_title")
    col2_1.text_area("**Bullet 1**", value=bullet_1, on_change=update_session_upload_listing, args=(mba_upload_data, ), key="mba_upload_listing_bullet_1")
    col2_1.text_area("**Description**", value=description, on_change=update_session_upload_listing, args=(mba_upload_data, ), key="mba_upload_listing_description")
    # Column 2
    col2_2.text_area("**Brand**", value=brand, on_change=update_session_upload_listing, args=(mba_upload_data, ), key="mba_upload_listing_brand")
    col2_2.text_area("**Bullet 2**", value=bullet_2, on_change=update_session_upload_listing, args=(mba_upload_data, ), key="mba_upload_listing_bullet_2")

    # cold start
    if mba_upload_data.title == None:
        update_session_upload_listing(mba_upload_data)

def update_session_upload_listing(mba_upload_data: MBAUploadData):
    # Update data
    mba_upload_data.brand = st.session_state["mba_upload_listing_brand"]
    mba_upload_data.title = st.session_state["mba_upload_listing_title"]
    mba_upload_data.bullet_1 = st.session_state["mba_upload_listing_bullet_1"]
    mba_upload_data.bullet_2 = st.session_state["mba_upload_listing_bullet_2"]
    mba_upload_data.description = st.session_state["mba_upload_listing_description"]