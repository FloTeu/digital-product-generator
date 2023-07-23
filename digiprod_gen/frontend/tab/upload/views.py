import streamlit as st

from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display
from digiprod_gen.backend.data_classes.session import MBAUploadData, SessionState
from collections import deque
from PIL import Image, ImageOps
from enum import Enum

class ListingSelectChange(str, Enum):
    TITLE="mba_upload_select_box_title"
    BRAND="mba_upload_select_box_brand"
    BULLET_1="mba_upload_select_box_bullet_1"
    BULLET_2="mba_upload_select_box_bullet_2"

def display_listing_selection(predicted_titles, predicted_brands, predicted_bullets, tab_crawling):
    st.subheader("Suggested Product Listing")
    st.selectbox("Suggested Titles:", predicted_titles, on_change=update_session_upload_listing, args=(ListingSelectChange.TITLE, ), key=ListingSelectChange.TITLE.value)
    
    st.selectbox("Suggested Brands:", predicted_brands, on_change=update_session_upload_listing, args=(ListingSelectChange.BRAND, ), key=ListingSelectChange.BRAND.value)

    st.selectbox("Suggested Bullet 1:", predicted_bullets, on_change=update_session_upload_listing, args=(ListingSelectChange.BULLET_1, ), key=ListingSelectChange.BULLET_1.value)
    # put first element to end of list
    predicted_bullets_shifted = deque(predicted_bullets)
    predicted_bullets_shifted.rotate(-1)
    st.selectbox("Suggested Bullet 2:", predicted_bullets_shifted, on_change=update_session_upload_listing, args=(ListingSelectChange.BULLET_2, ), key=ListingSelectChange.BULLET_2.value)

def display_upload_ready_image(img_pil: Image):
    new_size = (4500, 5400)
    image_pil_upload_ready = Image.new("RGBA", new_size)

    box = tuple((n - o) // 2 for n, o in zip(new_size, img_pil.size))
    image_pil_upload_ready.paste(img_pil, (box[0], 0))

    image_to_show = ImageOps.expand(image_pil_upload_ready, border=50, fill='grey')
    st.image(image_to_show)

    # update session image
    session_state: SessionState = st.session_state["session_state"]
    session_state.image_gen_data.image_pil_upload_ready = image_pil_upload_ready

def display_data_for_upload(image_pil, title, brand, bullet_1, bullet_2):
    st.subheader("Upload Overview")
    col1, col2 = st.columns(2)
    col2_1, col2_2 = col2.columns(2)

    with col1:
        display_upload_ready_image(image_pil)

    session_state: SessionState = st.session_state["session_state"]
    mba_upload_data: MBAUploadData = session_state.upload_data

    if not mba_upload_data.description and title:
        description = f'{title} by "{brand}". {bullet_1} {bullet_2}'
    else:
        description = "" if mba_upload_data.description == None else mba_upload_data.description

    # Column 1
    col2_1.text_area("**Title**", value=title, on_change=update_session_upload_listing, key="mba_upload_listing_title")
    col2_1.text_area("**Bullet 1**", value=bullet_1, on_change=update_session_upload_listing, key="mba_upload_listing_bullet_1")
    col2_1.text_area("**Description**", value=description, on_change=update_session_upload_listing, disabled=True, key="mba_upload_listing_description")

    # Column 2
    col2_2.text_area("**Brand**", value=brand, on_change=update_session_upload_listing, key="mba_upload_listing_brand")
    col2_2.text_area("**Bullet 2**", value=bullet_2, on_change=update_session_upload_listing, key="mba_upload_listing_bullet_2")

    # cold start
    if mba_upload_data.title == None:
        update_session_upload_listing()

def update_session_upload_listing(listing_select_change: ListingSelectChange | None = None):
    session_state: SessionState = st.session_state["session_state"]
    mba_upload_data: MBAUploadData = session_state.upload_data

    # Update data
    # Either take the select box text or the input text depending on what was updated by user
    mba_upload_data.brand = st.session_state[listing_select_change.value] if listing_select_change == ListingSelectChange.BRAND else st.session_state["mba_upload_listing_brand"]
    mba_upload_data.title = st.session_state[listing_select_change.value] if listing_select_change == ListingSelectChange.TITLE else st.session_state["mba_upload_listing_title"]
    mba_upload_data.bullet_1 = st.session_state[listing_select_change.value] if listing_select_change == ListingSelectChange.BULLET_1 else st.session_state["mba_upload_listing_bullet_1"]
    mba_upload_data.bullet_2 = st.session_state[listing_select_change.value] if listing_select_change == ListingSelectChange.BULLET_2 else st.session_state["mba_upload_listing_bullet_2"]
    mba_upload_data.description = f'{mba_upload_data.title} by "{mba_upload_data.brand}". {mba_upload_data.bullet_1} {mba_upload_data.bullet_2}'