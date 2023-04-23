
import streamlit as st
import os, sys

from digiprod_gen.backend.image import conversion as img_conversion
from digiprod_gen.frontend.session import read_session, update_mba_request
from digiprod_gen.frontend import sidebar
from digiprod_gen.frontend.tab.image_generation.selected_products import get_selected_mba_products_by_url
from digiprod_gen.frontend.tab.image_generation.selected_products import display_mba_products
from digiprod_gen.frontend.tab.image_generation.image_editing import get_image_bytes_by_user, display_image_editor
from digiprod_gen.frontend.tab.upload.bullet_selection import display_bullet_selection
from digiprod_gen.frontend.tab.upload.mba_upload import login_to_mba, display_mba_account_tier

@st.experimental_singleton
def installff():
  os.system('sbase install geckodriver')
  os.system('ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')

_ = installff()
st.header("MBA Bullet Feature Extractor")
tab_crawling, tab_ig, tab_upload = st.tabs(["Crawling", "Image Generation", "MBA Upload"])

def read_request():
    request = read_session("request")
    if request == None:
        update_mba_request()
        request = read_session("request")
    return request

def main():
    sidebar.crawling_mba_overview_input(tab_crawling)
    request = read_request()

    mba_products = read_session([request.get_hash_str(), "mba_products"])
    if mba_products != None:
        sidebar.crawling_mba_details_input(mba_products, tab_crawling, tab_ig)

        mba_products_selected = get_selected_mba_products_by_url(request)
        if mba_products_selected and read_session([request.get_hash_str(), "detail_pages_crawled"]):
            sidebar.prompt_generation_input(tab_crawling, tab_ig)
            predicted_prompts = read_session([request.get_hash_str(), "predicted_prompts"])
            predicted_bullets = read_session([request.get_hash_str(), "predicted_bullets"])
            display_mba_products(tab_ig, mba_products_selected)
            if predicted_prompts:
                with tab_ig:
                    st.subheader("Suggested Prompts")
                    st.write(predicted_prompts)
                    image: bytes | None = get_image_bytes_by_user()
                    if image:
                        image_pil = img_conversion.bytes2pil(image)
                        print("type", type(image_pil))
                        image_pil_upload_ready = display_image_editor(image_pil)

            if predicted_bullets:
                with tab_upload:
                    display_bullet_selection(predicted_bullets, tab_crawling)

    # just for debuging
    image: bytes | None = get_image_bytes_by_user()
    if image:
        
        mba_email = st.sidebar.text_input("MBA Email:")
        mba_password = st.sidebar.text_input("MBA Password:", type="password")
        driver = read_session("selenium_driver")
        if st.sidebar.button("Login") and mba_email and mba_password:
            driver = login_to_mba(mba_email, mba_password)
        from digiprod_gen.backend.upload import selenium_mba
        from digiprod_gen.frontend.session import write_session
        if driver and "verification" in driver.page_source.lower():
            otp_code = st.sidebar.text_input("OTP")
            if st.sidebar.button("Send OTP Token") and otp_code:
                selenium_mba.authenticate_mba_with_opt_code(driver, otp_code)
                write_session("selenium_driver", driver)

            if not "verification" in driver.page_source.lower():
                display_mba_account_tier(driver)

        # import mechanize
        # import requests
        # from robobrowser import RoboBrowser

        # image_pil = img_conversion.bytes2pil(image)
        # print("type", type(image_pil))
        # image_pil_upload_ready = display_image_editor(image_pil)
        
        # # from twill import browser
        # login_post_url = "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=3600&openid.return_to=https%3A%2F%2Fmerch.amazon.com%2Fdashboard&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=amzn_gear_us&openid.mode=checkid_setup&language=en_US&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
        # # browser.go(mba_url)
        # # browser.show_forms()
        # username = st.secrets.mba.user_name
        # password = st.secrets.mba.password
        # #login_post_url = "http://www.naturalgasintel.com/user/login"
        # internal_url = "https://merch.amazon.com/dashboard"
        # r = requests.get(internal_url, headers=request.headers)
        # login_post_url = r.url

        # # mechanical soup
        # import mechanicalsoup
        # from requests_html import HTMLSession, AsyncHTMLSession, run_in_thread
        # import asyncio
        # import threading
        # # Define a function to render the HTML with JavaScript

        # def render_html(session, url, headers):
        #     response = session.get(url, headers=headers)
        #     response.html.render(sleep=2)
        #     return response.html.html


        # browser = mechanicalsoup.StatefulBrowser()

        # # Create a new session object from requests-html
        # session = HTMLSession()
        # asession = AsyncHTMLSession()


        # response_login = browser.open(login_post_url, headers=request.headers)
        # browser.select_form('form[name="signIn"]')
        # #browser.form.print_summary()

        # # login
        # browser["email"] = username
        # browser["password"] = password
        # #browser.launch_browser()
        # response_otp = browser.submit_selected(headers=request.headers)
        # if "verification" in response_otp.text.lower():
        #     second_factor_code = st.sidebar.number_input("2FA Code:")
        #     browser.select_form('form[id="auth-mfa-form"]')
        #     browser["otpCode"] = second_factor_code
        #     browser["rememberDevice"] = True
        #     response_dashboard = browser.submit_selected(headers=request.headers)

        #     # Wait for the content to be rendered
        #     session.cookies.update(browser.session.cookies.get_dict())
        #     #response = session.get(browser.get_url(), headers=request.headers)
        #     #response.html.render(sleep=2)

        #     # Start a new thread to run the rendering function
        #     t = threading.Thread(target=render_html, args=(session, browser.get_url(), request.headers))
        #     t.start()
        #     # Wait for the thread to finish
        #     t.join()

        #     # Read the rendered HTML content
        #     rendered_html = t.result()

        #     # loop = asyncio.new_event_loop()
        #     # asyncio.set_event_loop(loop)
        #     # loop.run_until_complete(response.html.arender(timeout=10))






if __name__ == "__main__":
    main()















