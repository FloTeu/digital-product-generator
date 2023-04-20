import streamlit as st

def crawling_input():
    st.sidebar.subheader("1. Crawling MBA Overview")
    st.sidebar.checkbox(label="Speed up Crawling", value=True, key="is_debug")
    st.sidebar.text_input(value="Pew Pew Madafakas", label="Search Term", on_change=update_mba_request, key="search_term")
    st.sidebar.selectbox("MBA Marketplace",
                                       options=[MBAMarketplaceDomain.COM, MBAMarketplaceDomain.DE], on_change=update_mba_request, key="marketplace")
