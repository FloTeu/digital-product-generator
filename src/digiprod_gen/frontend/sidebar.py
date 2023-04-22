import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from digiprod_gen.frontend.session import update_mba_request
from digiprod_gen.backend.data_classes import MBAMarketplaceDomain
from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display
from digiprod_gen.frontend.tab.image_generation.selected_products import crawl_details_update_overview_page
from digiprod_gen.frontend.tab.image_generation.prompt_generation import prompt_generation_refresh_overview


def crawling_mba_overview_input(tab_crawling: DeltaGenerator):
    st.sidebar.subheader("1. Crawling MBA Overview")
    st.sidebar.checkbox(label="Speed up Crawling", value=True, key="is_debug")
    st.sidebar.text_input(value="Pew Pew Madafakas", label="Search Term", on_change=update_mba_request, key="search_term")
    st.sidebar.selectbox("MBA Marketplace",
                                       options=[MBAMarketplaceDomain.COM, MBAMarketplaceDomain.DE], on_change=update_mba_request, key="marketplace")
    st.sidebar.button("Start Crawling", on_click=crawl_mba_overview_and_display, args=(tab_crawling, ))


def crawling_mba_details_input(mba_products, tab_crawling: DeltaGenerator, tab_ig: DeltaGenerator):
    st.sidebar.subheader("2. Crawling MBA Product Pages")
    st.sidebar.multiselect("Select Designs for prompt generation:", [i+1 for i in range(len(mba_products))], key='selected_designs', on_change=crawl_mba_overview_and_display, args=(tab_crawling, ))
    st.sidebar.button("Start Crawling Details", on_click=crawl_details_update_overview_page, args=(tab_ig, tab_crawling, ), key="button_crawl_detail")


def prompt_generation_input(tab_crawling: DeltaGenerator, tab_ig: DeltaGenerator):
    st.sidebar.subheader("3. Prompt Generation")
    st.sidebar.button("Start Prompt Generation", on_click=prompt_generation_refresh_overview, args=(tab_ig, tab_crawling, ), key="button_prompt_generation")




