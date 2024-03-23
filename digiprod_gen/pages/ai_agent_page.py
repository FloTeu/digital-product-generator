import streamlit as st
from digiprod_gen.backend.image import conversion
from digiprod_gen.backend.models.session import SessionState
from digiprod_gen.frontend.session import read_session
from digiprod_gen.frontend.sidebar import display_page_navigation
from digiprod_gen.pages.manual_page import display_full_page_screenshot

def main():
    st.header("MBA Product Generator")
    session_state: SessionState = st.session_state["session_state"]

    # display views (+ add defaults to session)

    sidebar_element = session_state.views.get_or_create_sidebar()
    # before re rendering, empty all existing views
    sidebar_element.empty()

    with sidebar_element.container():
        display_page_navigation()



if __name__ == "__main__":
    main()

