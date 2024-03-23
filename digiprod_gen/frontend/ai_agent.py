import streamlit as st
from digiprod_gen.backend.models.session import SessionState, CrawlingData
from digiprod_gen.frontend.session import update_mba_request


def run_ai_agent_product_generation():
    """
    Takes a search term runs an ai agent with the following steps:
        1. Crawling
        2. Select matching designs
        3. Prompt generation
        4. Image generation
        5. Export to file system
    """
    session_state: SessionState = st.session_state["session_state"]

    # If not set yet, init session request
    if session_state.crawling_request == None:
        update_mba_request()

    st.write("Success!!")
