
import streamlit as st
import os, sys
import digiprod_gen

from selenium.common.exceptions import WebDriverException

from digiprod_gen.backend.utils import is_debug
from digiprod_gen.backend.image import conversion as img_conversion
from digiprod_gen.backend.data_classes import CrawlingMBARequest, DigiProdGenConfig
from digiprod_gen.backend.upload.selenium_mba import upload_image, click_on_create_new, insert_listing_text, select_products_and_marketplaces, publish_to_mba
from digiprod_gen.frontend.session import read_session, update_mba_request, write_session
from digiprod_gen.frontend import sidebar
from digiprod_gen.frontend.tab.image_generation.selected_products import get_selected_mba_products_by_url
from digiprod_gen.frontend.tab.image_generation.selected_products import display_mba_products
from digiprod_gen.frontend.tab.image_generation.image_editing import get_image_bytes_by_user, display_image_editor
from digiprod_gen.frontend.tab.upload.views import display_listing_selection, display_data_for_upload
from digiprod_gen.frontend.tab.upload.mba_upload import login_to_mba, display_mba_account_tier

os.environ["OPENAI_API_KEY"] = st.secrets["open_ai_api_key"]

st.header("MBA Product Generator")
tab_crawling, tab_ig, tab_upload = st.tabs(["Crawling", "Image Generation", "MBA Upload"])

def read_request():
    request = read_session("request")
    if request == None:
        update_mba_request()
        request = read_session("request")
    return request

def main():
    sidebar.crawling_mba_overview_input(tab_crawling)
    request: CrawlingMBARequest = read_request()
    predicted_bullets = None
    
    mba_products = read_session([request.get_hash_str(), "mba_products"])
    if mba_products != None:
        sidebar.crawling_mba_details_input(mba_products, tab_crawling, tab_ig)

        mba_products_selected = get_selected_mba_products_by_url(request)
        if mba_products_selected and read_session([request.get_hash_str(), "detail_pages_crawled"]):
            sidebar.prompt_generation_input(tab_crawling, tab_ig)
            predicted_prompts = read_session([request.get_hash_str(), "predicted_prompts"])
            predicted_prompt = read_session([request.get_hash_str(), "predicted_prompt"])
            predicted_bullets = read_session([request.get_hash_str(), "predicted_bullets"])
            predicted_titles = read_session([request.get_hash_str(), "predicted_titles"])
            predicted_brands = read_session([request.get_hash_str(), "predicted_brands"])

            display_mba_products(tab_ig, mba_products_selected)
            if predicted_prompts:
                with tab_ig:
                    st.subheader("Suggested Prompts")
                    st.write(predicted_prompt)
                    st.write(predicted_prompts)
                    image_bytes: bytes | None = get_image_bytes_by_user()
                    if image_bytes:
                        image_pil = img_conversion.bytes2pil(image_bytes)
                        print("type", type(image_pil))
                        image_pil_upload_ready = display_image_editor(image_pil, background_removal_buffer=0)
                        if image_pil_upload_ready:
                            write_session([request.get_hash_str(), "image_pil_upload_ready"], image_pil_upload_ready)



    sidebar.mab_login_input(tab_upload)
    driver = read_session("selenium_driver")
    try:
        sidebar.mba_otp_input(driver)
    except WebDriverException:
        # TODO: Find out why this error is thrown
        pass
        
    with tab_upload:
        image_pil_upload_ready = read_session([request.get_hash_str(), "image_pil_upload_ready"])
        # User can either choose newly created image or choose a existing one
        if not image_pil_upload_ready:
            image = st.file_uploader("Image:", type=["png", "jpg", "jpeg"], key="image_upload_tab")
            if image:
                image_pil_upload_ready = img_conversion.bytes2pil(image.getvalue())
                write_session([request.get_hash_str(), "image_pil_upload_ready"], image_pil_upload_ready)
        
        if predicted_bullets and predicted_brands and predicted_titles:
            display_listing_selection(predicted_titles, predicted_brands, predicted_bullets, tab_crawling)

        if image_pil_upload_ready:
            predicted_description = f'{read_session("mba_upload_title")} by "{read_session("mba_upload_brand")}". {read_session("mba_upload_bullet_1")} {read_session("mba_upload_bullet_2")}'
            display_data_for_upload(image_pil_upload_ready, title=read_session("mba_upload_title"), brand=read_session("mba_upload_brand"), bullet_1=read_session("mba_upload_bullet_1"), bullet_2=read_session("mba_upload_bullet_2"), description=predicted_description)

        if read_session("mba_login_successfull"):
            display_mba_account_tier(driver)
            if st.button("Upload product to MBA"):
                click_on_create_new(driver)
                select_products_and_marketplaces(driver, products=[request.product_category] , marketplaces=[request.marketplace])
                upload_image(driver, image_pil_upload_ready)
                if read_session("mba_upload_bullet_1") and read_session("mba_upload_bullet_2"):
                    st.error('You not defined your listings yet', icon="🚨")
                else:
                    # TODO: how to handle case with Marketplace different to com (language of bullets is german for example but form takes englisch text input)
                    insert_listing_text(driver, title=read_session("mba_upload_title"), brand=read_session("mba_upload_brand"), bullet_1=read_session("mba_upload_bullet_1"), bullet_2=read_session("mba_upload_bullet_2"), description=predicted_description)
                    #publish_to_mba(searchable=not is_debug())




if __name__ == "__main__":
    main()



