from digiprod_gen.frontend.session import read_session
from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display


import streamlit as st


from collections import deque


def display_bullet_selection(predicted_bullets, tab_crawling):
    st.subheader("Suggested Bullets")
    st.selectbox("Bullet 1:", predicted_bullets, on_change=crawl_mba_overview_and_display, args=(tab_crawling, ), key="bullet1")
    predicted_bullets_shifted = deque(predicted_bullets)
    predicted_bullets_shifted.rotate(-1)
    st.selectbox("Bullet 2:", predicted_bullets_shifted, on_change=crawl_mba_overview_and_display, args=(tab_crawling, ), key="bullet2")
    st.text_area("Bullet 1:", value=read_session("bullet1"))
    st.text_area("Bullet 2:", value=read_session("bullet2"))