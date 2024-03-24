import streamlit as st

from digiprod_gen.backend.browser.selenium_fns import get_full_page_screenshot
from digiprod_gen.backend.image import conversion
from digiprod_gen.backend.models.session import SessionState
from digiprod_gen.frontend.session import read_session
from digiprod_gen.frontend.sidebar import display_page_navigation

def display_full_page_screenshot(driver):
    screenshot_bytes = get_full_page_screenshot(driver)
    screenshot_pil = conversion.bytes2pil(screenshot_bytes)
    st.image(screenshot_pil)

def display_admin_views():
    """Display some options for the admin"""

    session_state: SessionState = read_session("session_state")
    if st.experimental_user.email in st.secrets.admin.emails or read_session("mba_email") in st.secrets.admin.emails:
        st.subheader("Admin View")
        st.warning("Note: This is only visible to admins")

        url = st.text_input("Url")
        if st.button("Browse url"):
            response = session_state.backend_caller.get(
                f"/browser/browse?url={url}&session_id={session_state.session_id}&proxy={session_state.crawling_request.proxy}")

        if st.button("Show Browser Screenshot (API)"):
            response = session_state.backend_caller.get(
                f"/status/browser_screenshot?session_id={session_state.session_id}&proxy={session_state.crawling_request.proxy}")
            browser_screenshot_pil = conversion.bytes2pil(response.content)
            st.image(browser_screenshot_pil)

        if st.button("Show Browser Settings (API)"):
            response = session_state.backend_caller.get(
                f"/status/browser_settings?session_id={session_state.session_id}&proxy={session_state.crawling_request.proxy}")
            st.text(response.json())

        if session_state.browser:
            if st.button("Show Browser Screenshot (Frontend)"):
                display_full_page_screenshot(session_state.browser.driver)
            st.download_button('Download Browser Source', session_state.browser.driver.page_source, file_name="source.html")

        if st.button("Send Select Products Request"):
            from digiprod_gen.backend.image.conversion import bytes2pil, pil2b64_str
            from digiprod_gen.frontend.tab.crawling.views import mba_products_overview_html_str
            import imgkit

            if session_state.crawling_data.mba_products:
                from pydantic import BaseModel
                from digiprod_gen.backend.models.mba import MBAProduct
                from typing import List

                class MBAProductsRequest(BaseModel):
                    mba_products: List[MBAProduct]

                request_body = MBAProductsRequest(mba_products=session_state.crawling_data.mba_products)
                session_state.backend_caller.post("/research/select_products",
                                                  data=request_body.model_dump_json())

def main():
    st.header("MBA Product Generator")
    st.text_input("Admin Token", key="mba_email")
    session_state: SessionState = read_session("session_state")

    # display views (+ add defaults to session)
    display_admin_views()

    sidebar_element = session_state.views.get_or_create_sidebar()
    # before re rendering, empty all existing views
    sidebar_element.empty()

    with sidebar_element.container():
        display_page_navigation()



if __name__ == "__main__":
    main()

