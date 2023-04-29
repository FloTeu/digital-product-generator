from digiprod_gen.frontend.session import read_session
from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display


import streamlit as st

from collections import deque


def display_bullet_selection(predicted_bullets, tab_crawling):
    st.subheader("Suggested Bullets")
    st.selectbox("Bullet 1:", predicted_bullets, on_change=crawl_mba_overview_and_display, args=(tab_crawling, ), key="mba_upload_bullet_1")
    predicted_bullets_shifted = deque(predicted_bullets)
    predicted_bullets_shifted.rotate(-1)
    st.selectbox("Bullet 2:", predicted_bullets_shifted, on_change=crawl_mba_overview_and_display, args=(tab_crawling, ), key="mba_upload_bullet_2")

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
