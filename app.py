
import streamlit as st

from digiprod_gen.backend.image import conversion as img_conversion
from digiprod_gen.frontend.session import read_session, update_mba_request
from digiprod_gen.frontend import sidebar
from digiprod_gen.frontend.tab.image_generation.selected_products import get_selected_mba_products_by_url
from digiprod_gen.frontend.tab.image_generation.selected_products import display_mba_products
from digiprod_gen.frontend.tab.image_generation.image_editing import get_image_bytes_by_user, display_image_editor
from digiprod_gen.frontend.tab.upload.bullet_selection import display_bullet_selection

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

if __name__ == "__main__":
    main()















