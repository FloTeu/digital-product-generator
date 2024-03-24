import streamlit as st
from typing import List, Tuple

from selenium.common import NoSuchElementException

from digiprod_gen.backend.image import conversion as img_conversion, conversion
from digiprod_gen.backend.image.utils import hex_to_rgba
from digiprod_gen.backend.image.upscale import resize_image_keep_aspect_ratio
from digiprod_gen.backend.models.response import UploadMBAResponse
from digiprod_gen.backend.utils.decorators import timeit
from digiprod_gen.backend.utils.helper import Timer
from digiprod_gen.backend.models.session import MBAUploadData, SessionState, ImageGenData, DigiProdGenStatus
from digiprod_gen.backend.models.mba import MBAMarketplaceDomain, MBAProductCategory, MBAProductColor, \
    MBAProductFitType, MBAUploadSettings
from collections import deque
from PIL import Image, ImageOps
from enum import Enum

from digiprod_gen.frontend.session import read_session


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

def display_char_max_notice(n_chars: int, max_n_chars: int, st_element):
    if n_chars > max_n_chars:
        st_element.write(f":red[Chars: {n_chars} (max {max_n_chars})]")
    else:
        st_element.write(f"Chars: {n_chars} (max {max_n_chars})")

def display_data_for_upload(image_pil: Image,
                            title: str | None,
                            brand: str | None,
                            bullet_1: str | None,
                            bullet_2: str | None,
                            disable_all: bool = False,
                            key_suffix="",
                            change_session=True
                            ) -> Image:
    st.subheader("Upload Overview")
    col1, col2 = st.columns(2)
    col2_1, col2_2 = col2.columns(2)

    with Timer("display_upload_ready_image"), col1:
        color_hex = st.color_picker('Pick a background color', '#000000', key=f"cp{key_suffix}")
        rgba_tuple = hex_to_rgba(color_hex)

        # max_pixels: Defines the maximum number of pixel width for resize feature
        max_pixels = 6000
        value = float("%.2f" % (image_pil.size[0] / max_pixels))
        slider_value = st.slider("Scale image", min_value=0.0, max_value=1.0, value=value, step=0.01, key=f"s{key_suffix}")
        image_pil = resize_image_keep_aspect_ratio(image_pil, int(slider_value * max_pixels))
        try:
            display_upload_ready_image(image_pil, rgba_tuple)
        except Exception as e:
            st.warning(f"Could not display image {e}")
    session_state: SessionState = st.session_state["session_state"]
    mba_upload_data: MBAUploadData = session_state.upload_data

    if not mba_upload_data.description and title:
        description = f'{title} by "{brand}". {bullet_1} {bullet_2}'
    else:
        description = "" if mba_upload_data.description == None else mba_upload_data.description

    # Column 1
    if title:
        final_title = col2_1.text_area("**Title**", value=title, on_change=update_session_upload_listing, disabled=disable_all, key=f"mba_upload_listing_title{key_suffix}")
        display_char_max_notice(len(final_title), 60, col2_1)
        if change_session:
            st.session_state["final_title"] = final_title
        mba_upload_data.title = final_title
    if bullet_1:
        final_bullet1 = col2_1.text_area("**Bullet 1**", value=bullet_1, on_change=update_session_upload_listing, disabled=disable_all, key=f"mba_upload_listing_bullet_1{key_suffix}")
        display_char_max_notice(len(final_bullet1), 256, col2_1)
        if change_session:
           st.session_state["final_bullet1"] = final_bullet1
        mba_upload_data.bullet_1 = final_bullet1
    if title and brand:
        # Note: Description is automatically updated within update_session_upload_listing
        col2_1.text_area("**Description**", value=description, on_change=update_session_upload_listing, disabled=True, key=f"mba_upload_listing_description{key_suffix}")



    # Column 2
    if brand:
        final_brand = col2_2.text_area("**Brand**", value=brand, on_change=update_session_upload_listing, disabled=disable_all, key=f"mba_upload_listing_brand{key_suffix}")
        display_char_max_notice(len(final_brand), 50, col2_2)
        if change_session:
           st.session_state["final_brand"] = final_brand
        mba_upload_data.brand = final_brand
    if bullet_2:
        final_bullet2 = col2_2.text_area("**Bullet 2**", value=bullet_2, on_change=update_session_upload_listing, disabled=disable_all, key=f"mba_upload_listing_bullet_2{key_suffix}")
        display_char_max_notice(len(final_bullet2), 256, col2_2)
        if change_session:
           st.session_state["final_bullet2"] = final_bullet2
        mba_upload_data.bullet_2 = final_bullet2

    # Update description with latest changes
    try:
        mba_upload_data.description = f'{mba_upload_data.title} by "{mba_upload_data.brand}". {mba_upload_data.bullet_1} {mba_upload_data.bullet_2}'
    except Exception as e:
        print("Error during description creation", str(e))
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
        mba_upload_data.brand = st.session_state["final_brand"] if "final_brand" in st.session_state else None
        mba_upload_data.title = st.session_state["final_title"] if "final_title" in st.session_state else None
        mba_upload_data.bullet_1 = st.session_state["final_bullet1"] if "final_bullet1" in st.session_state else None
        mba_upload_data.bullet_2 = st.session_state["final_bullet2"] if "final_bullet2" in st.session_state else None
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

def display_image_uploader(image_gen_data: ImageGenData, status: DigiProdGenStatus):
    # User can either choose newly created image or a existing one (by uploading it in this view)
    if not status.image_upload_ready and not status.product_imported:
        image = st.file_uploader("Image:", type=["png", "jpg", "jpeg"], key="image_upload_tab")
        if image:
            image_pil_upload_ready = img_conversion.bytes_io2pil(image)
            image_gen_data.image_pil_upload_ready = img_conversion.pil2pil_png(image_pil_upload_ready)


def upload_product(session_state):
    errors = []
    with st.spinner("Upload product"):
        try:
            if session_state.upload_data.title == None or session_state.upload_data.brand == None:
                st.error('You not defined your required brand and title yet', icon="🚨")
                session_state.upload_data.title = "Test Title"
                session_state.upload_data.brand = "Test Brand"
            if session_state.upload_data.bullet_1 == None and session_state.upload_data.bullet_2 == None:
                st.error('You not defined your listings yet', icon="🚨")

            headers = {
                'accept': 'application/json',
            }
            request_data = {**session_state.upload_data.settings.model_dump(), "title": session_state.upload_data.title,
                            "brand": session_state.upload_data.brand, "bullet_1": session_state.upload_data.bullet_1,
                            "bullet_2": session_state.upload_data.bullet_2,
                            "description": session_state.upload_data.description}
            response = session_state.backend_caller.post(
                f"/browser/upload/upload_mba_product?session_id={session_state.session_id}&proxy={session_state.crawling_request.proxy}",
                headers=headers, data=request_data, img_pil=session_state.image_gen_data.image_pil_upload_ready
            )
            if response.status_code == 200:
                upload_response: UploadMBAResponse = UploadMBAResponse.parse_obj(response.json())
                warnings = upload_response.warnings
                errors = upload_response.errors
                if len(warnings) == 0 and len(errors) == 0:
                    session_state.status.product_uploaded = True
            else:
                warnings, errors = [], []
        except NoSuchElementException as e:
            st.error("Something went wrong during upload")
            raise e
    for warning in warnings:
        st.warning(f"MBA Warning: {warning}")
    for error in errors:
        st.error(f"MBA Error: {error}")
    return errors


def display_tab_upload_views(session_state: SessionState):
    display_image_uploader(session_state.image_gen_data, session_state.status)

    # listing generation
    if not session_state.status.listing_generated:
        st.warning('Please click on 4. Listing Generation')


    if session_state.status.listing_generated:
        display_listing_selection(session_state.upload_data)

        display_img = session_state.image_gen_data.image_pil_upload_ready
        if display_img is None and session_state.status.product_imported:
            display_img = session_state.image_gen_data.image_pil_generated

        if display_img:
            session_state.image_gen_data.image_pil_upload_ready = display_data_for_upload(conversion.ensure_rgba(display_img),
                                    title=read_session("final_title") or read_session(ListingSelectChange.TITLE.value),
                                    brand=read_session("final_brand") or read_session(ListingSelectChange.BRAND.value),
                                    bullet_1=read_session("final_bullet1") or read_session(ListingSelectChange.BULLET_1.value),
                                    bullet_2=read_session("final_bullet2") or read_session(ListingSelectChange.BULLET_2.value))

            is_download_visible = st.checkbox("Activate Download Image Button", key="download_final_upload_ready_image")
            if is_download_visible:
                with st.spinner("Load Download Button"):
                    st.download_button("Download Image", data=conversion.pil2bytes_io(session_state.image_gen_data.image_pil_upload_ready),
                                         file_name=f"export.{session_state.image_gen_data.image_pil_upload_ready.format}",
                                         mime=f'image/{session_state.image_gen_data.image_pil_upload_ready.format}', use_container_width=True)

    mba_upload_settings = session_state.upload_data.settings
    display_marketplace_selector(mba_upload_settings)

    use_defaults = st.checkbox("Use MBA defaults")
    mba_upload_settings.use_defaults = use_defaults
    if not use_defaults:
        display_product_category_selector(mba_upload_settings)
        display_product_color_selector(mba_upload_settings)
        display_product_fit_type_selector(mba_upload_settings)

    #if session_state.status.detail_pages_crawled:
    if not session_state.status.mba_login_successful:
        st.warning("Please login with your MBA credentials (5. MBA Upload)")
    else:
        #display_mba_account_tier(session_state.browser.driver)
        errors = []
        # Image Upload
        if session_state.image_gen_data.image_pil_upload_ready == None:
            st.error('You not uploaded/generated an image yet', icon="🚨")
        else:
            if st.button("Upload product to MBA"):
                errors = upload_product(session_state)
            if len(errors) == 0 and session_state.status.product_uploaded and st.button("Publish to MBA"):
                response = session_state.backend_caller.get(
                    f"/browser/upload/publish_mba_product?session_id={session_state.session_id}&proxy={session_state.crawling_request.proxy}&searchable=true"
                )
                if response.status_code == 200:
                    st.balloons()
                else:
                    st.error("Something went wrong during publishing")
