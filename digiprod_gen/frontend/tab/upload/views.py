import streamlit as st
from typing import List, Tuple

from digiprod_gen.backend.image import conversion as img_conversion
from digiprod_gen.backend.image.utils import hex_to_rgba
from digiprod_gen.backend.image.upscale import resize_image_keep_aspect_ratio
from digiprod_gen.backend.utils.helper import Timer
from digiprod_gen.backend.models.session import MBAUploadData, SessionState, ImageGenData, DigiProdGenStatus
from digiprod_gen.backend.models.mba import MBAMarketplaceDomain, MBAProductCategory, MBAProductColor, \
    MBAProductFitType, MBAUploadSettings
from collections import deque
from PIL import Image, ImageOps
from enum import Enum

class ListingSelectChange(str, Enum):
    TITLE="mba_upload_select_box_title"
    BRAND="mba_upload_select_box_brand"
    BULLET_1="mba_upload_select_box_bullet_1"
    BULLET_2="mba_upload_select_box_bullet_2"

def display_listing_selection(upload_data: MBAUploadData):
    st.subheader("Suggested Product Listing")
    st.selectbox("Suggested Titles:", upload_data.predicted_titles, on_change=update_session_upload_listing, args=(ListingSelectChange.TITLE, ), key=ListingSelectChange.TITLE.value)
    
    st.selectbox("Suggested Brands:", upload_data.predicted_brands, on_change=update_session_upload_listing, args=(ListingSelectChange.BRAND, ), key=ListingSelectChange.BRAND.value)

    st.selectbox("Suggested Bullet 1:", upload_data.predicted_bullets, on_change=update_session_upload_listing, args=(ListingSelectChange.BULLET_1, ), key=ListingSelectChange.BULLET_1.value)
    # put first element to end of list
    predicted_bullets_shifted = deque(upload_data.predicted_bullets)
    predicted_bullets_shifted.rotate(-1)
    st.selectbox("Suggested Bullet 2:", predicted_bullets_shifted, on_change=update_session_upload_listing, args=(ListingSelectChange.BULLET_2, ), key=ListingSelectChange.BULLET_2.value)

def display_upload_ready_image(img_pil: Image, background_color: Tuple[int,int,int,int] = (255, 255, 255, 255)):
    new_size = (4500, 5400)
    image_pil_upload_ready = Image.new("RGBA", new_size, background_color)

    box = tuple((n - o) // 2 for n, o in zip(new_size, img_pil.size))
    # overwrite pixels by img_pil but only if alpha channel is > 0
    image_pil_upload_ready.paste(img_pil, (box[0], 0), img_pil)

    # add grey border
    image_to_show = ImageOps.expand(image_pil_upload_ready, border=50, fill='grey')
    resize_tuple = (int(new_size[0]/10), int(new_size[1]/10))
    st.image(image_to_show.resize(resize_tuple))

def display_data_for_upload(image_pil: Image,
                            title: str | None,
                            brand: str | None,
                            bullet_1: str | None,
                            bullet_2: str | None
                            ) -> Image:
    st.subheader("Upload Overview")
    col1, col2 = st.columns(2)
    col2_1, col2_2 = col2.columns(2)

    with Timer("display_upload_ready_image"), col1:
        color_hex = st.color_picker('Pick a background color', '#000000')
        rgba_tuple = hex_to_rgba(color_hex)

        # max_pixels: Defines the maximum number of pixel width for resize feature
        max_pixels = 6000
        value = float("%.2f" % (image_pil.size[0] / max_pixels))
        slider_value = st.slider("Scale image", min_value=0.0, max_value=1.0, value=value, step=0.01)
        image_pil = resize_image_keep_aspect_ratio(image_pil, int(slider_value * max_pixels))
        try:
            display_upload_ready_image(image_pil, rgba_tuple)
        except:
            st.warning("Could not display image")
    session_state: SessionState = st.session_state["session_state"]
    mba_upload_data: MBAUploadData = session_state.upload_data

    if not mba_upload_data.description and title:
        description = f'{title} by "{brand}". {bullet_1} {bullet_2}'
    else:
        description = "" if mba_upload_data.description == None else mba_upload_data.description

    # Column 1
    if title:
        final_title = col2_1.text_area("**Title**", value=title, on_change=update_session_upload_listing, key="mba_upload_listing_title")
        st.session_state["final_title"] = final_title
        mba_upload_data.title = final_title
    if bullet_1:
        final_bullet1 = col2_1.text_area("**Bullet 1**", value=bullet_1, on_change=update_session_upload_listing, key="mba_upload_listing_bullet_1")
        st.session_state["final_bullet1"] = final_bullet1
        mba_upload_data.bullet_1 = final_bullet1
    if title and brand:
        # Note: Description is automatically updated within update_session_upload_listing
        col2_1.text_area("**Description**", value=description, on_change=update_session_upload_listing, disabled=True, key="mba_upload_listing_description")



    # Column 2
    if brand:
        final_brand = col2_2.text_area("**Brand**", value=brand, on_change=update_session_upload_listing, key="mba_upload_listing_brand")
        st.session_state["final_brand"] = final_brand
        mba_upload_data.brand = final_brand
    if bullet_2:
        final_bullet2 = col2_2.text_area("**Bullet 2**", value=bullet_2, on_change=update_session_upload_listing, key="mba_upload_listing_bullet_2")
        st.session_state["final_bullet2"] = final_bullet2
        mba_upload_data.bullet_2 = final_bullet2


    # cold start
    if mba_upload_data.title == None:
        update_session_upload_listing()

    # Return image which might changes due to resize
    return image_pil

def update_session_upload_listing(listing_select_change: ListingSelectChange | None = None):
    """TODO Rethink lisintg update process. Currently to complicated"""
    print("update_session_upload_listing", listing_select_change)
    session_state: SessionState = st.session_state["session_state"]
    mba_upload_data: MBAUploadData = session_state.upload_data
    if listing_select_change == None:
        mba_upload_data.brand = st.session_state["final_brand"]
        mba_upload_data.title = st.session_state["final_title"]
        mba_upload_data.bullet_1 = st.session_state["final_bullet1"]
        mba_upload_data.bullet_2 = st.session_state["final_bullet2"]
    else:
        print(st.session_state[listing_select_change.value])
        latest_value = st.session_state[listing_select_change.value]

        # Update data
        # Either take the select box text or the input text depending on what was updated by user
        if listing_select_change == ListingSelectChange.BRAND:
            mba_upload_data.brand = latest_value
            st.session_state["final_brand"] = latest_value

        elif listing_select_change == ListingSelectChange.TITLE:
            mba_upload_data.title = latest_value
            st.session_state["final_title"] = latest_value

        elif listing_select_change == ListingSelectChange.BULLET_1:
            mba_upload_data.bullet_1 = latest_value
            st.session_state["final_bullet1"] = latest_value

        elif listing_select_change == ListingSelectChange.BULLET_2:
            mba_upload_data.bullet_2 = latest_value
            st.session_state["final_bullet2"] = latest_value

    mba_upload_data.description = f'{mba_upload_data.title} by "{mba_upload_data.brand}". {mba_upload_data.bullet_1} {mba_upload_data.bullet_2}'


# TODO: check if this error still appears:
#       KeyError: 'st.session_state has no key "mba_upload_listing_brand", if session is not filled yet

def display_multiselect(label: str, options: List[str], values: List[str]):
    container = st.container()
    all_marketplaces = st.checkbox("Select all", key=label)
    if all_marketplaces:
        return container.multiselect(label, options, options)
    else:
        return container.multiselect(label, options, values)


def display_marketplace_selector(session_mba_upload_settings: MBAUploadSettings):
    session_mba_upload_settings.marketplaces = display_multiselect("MBA Marketplace",
                                                                       MBAMarketplaceDomain.to_list(),
                                                                       [MBAMarketplaceDomain.COM.value])

def display_product_category_selector(session_mba_upload_settings: MBAUploadSettings):
    session_mba_upload_settings.product_categories = display_multiselect("MBA Product Category",
                                                                       MBAProductCategory.to_list(),
                                                                       [MBAProductCategory.SHIRT.value])

def display_product_color_selector(session_mba_upload_settings: MBAUploadSettings):
    default_values = [MBAProductColor.BLACK.value, MBAProductColor.ASPHALT_GREY.value, MBAProductColor.NAVY_BLUE.value,
                      MBAProductColor.WHITE.value, MBAProductColor.BROWN.value, MBAProductColor.DARK_HEATHER_GREY.value,
                      MBAProductColor.HEATHER_BLUE.value, MBAProductColor.SILVER_GREY.value, MBAProductColor.SLATE_GREY]

    session_mba_upload_settings.colors = display_multiselect("MBA Product Colors",
                                                               MBAProductColor.to_list(),
                                                                default_values)


def display_product_fit_type_selector(session_mba_upload_settings: MBAUploadSettings):
    session_mba_upload_settings.fit_types = display_multiselect("MBA Product Fit Type",
                                                               MBAProductFitType.to_list(),
                                                        [MBAProductFitType.MEN.value, MBAProductFitType.WOMAN.value])

def display_upload_settings_editor(session_mba_upload_settings: MBAUploadSettings):
    display_marketplace_selector(session_mba_upload_settings)
    display_product_category_selector(session_mba_upload_settings)
    display_product_color_selector(session_mba_upload_settings)
    display_product_fit_type_selector(session_mba_upload_settings)

def display_image_upload(image_gen_data: ImageGenData, status: DigiProdGenStatus):
    # User can either choose newly created image or a existing one (by uploading it in this view)
    if not status.image_upload_ready:
        image = st.file_uploader("Image:", type=["png", "jpg", "jpeg"], key="image_upload_tab")
        if image:
            image_pil_upload_ready = img_conversion.bytes_io2pil(image)
            image_gen_data.image_pil_upload_ready = img_conversion.pil2pil_png(image_pil_upload_ready)


