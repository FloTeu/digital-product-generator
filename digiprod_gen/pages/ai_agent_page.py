import streamlit as st

from pathlib import Path
from digiprod_gen.backend.utils.decorators import timeit
from digiprod_gen.backend.models.session import SessionState, DigitProdGenTabs
from digiprod_gen.frontend.session import update_mba_request, read_session
from digiprod_gen.frontend import sidebar
from digiprod_gen.frontend.sidebar import display_page_navigation
from digiprod_gen.frontend.tab.image_generation.views import display_tab_image_gen_views
from digiprod_gen.frontend.tab.upload.views import (display_tab_upload_views)
from digiprod_gen.frontend.tab.crawling.tab_crawling import display_mba_overview_products
from digiprod_gen.frontend.tab.prod_import.views import display_tab_import_views


@timeit
def display_views(session_state: SessionState):
    """Renders views based on session data"""
    ai_agent_view = session_state.views.get_or_create_ai_agent()
    # before re rendering, empty all existing elements in view
    ai_agent_view.empty()
    with ai_agent_view.container():
        st.write("AI AGENT VIEW")

    with session_state.views.tabs.crawling:
        overview_designs_view = session_state.views.get_or_create_overview_designs()
        # before re rendering, empty all existing elements in view
        overview_designs_view.empty()

        with overview_designs_view.container():
            if session_state.status.overview_page_crawled:
                display_mba_overview_products(session_state.crawling_data, session_state.crawling_request, shirts_per_row=session_state.config.view.cards_per_row)

    # with session_state.views.tabs.image_gen:
    #     display_tab_image_gen_views(session_state)

    with session_state.views.tabs.upload:
        display_tab_upload_views(session_state)

    if Path("export/").exists():
        with session_state.views.tabs.import_prod:
            display_tab_import_views(session_state)



@timeit
def display_sidebar(session_state: SessionState, tab_crawling, tab_ig, tab_upload):
    """Renders sidebar elements based on session data"""
    sidebar_element = session_state.views.get_or_create_sidebar()
    # before re rendering, empty all existing views
    sidebar_element.empty()

    with sidebar_element.container():
        display_page_navigation()
        sidebar.ai_agent_input()

        # MBA Login
        sidebar.mab_login_input(tab_upload, number="2")
        if session_state.status.mba_login_otp_required:
            sidebar.mba_otp_input()


def main():
    st.header("MBA Product Generator")
    tab_crawling, tab_ig, tab_upload, tab_import = st.tabs(["Crawling", "Image Generation", "MBA Upload", "MBA Import"])
    session_state: SessionState = read_session("session_state")
    session_state.views.tabs = DigitProdGenTabs(crawling=tab_crawling, image_gen=tab_ig, upload=tab_upload, import_prod=tab_import)

    # display views (+ add defaults to session)
    display_sidebar(session_state, tab_crawling, tab_ig, tab_upload)
    display_views(session_state)

    # init session request
    if session_state.crawling_request == None:
        update_mba_request()


if __name__ == "__main__":
    main()