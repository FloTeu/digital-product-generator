from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display


import streamlit as st

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
    col2_1.markdown(f"""
        ### Title
        {title}
        ### Bullet 1
        {bullet_1}
        ### Description
        {description}
    """)
    col2_2.markdown(f"""
        ### Brand
        {brand}
        ### Bullet 2
        {bullet_2}
    """)
