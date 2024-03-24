import logging
import streamlit as st
from typing import Tuple
from pathlib import Path
from glob import glob
from PIL import Image
from st_clickable_images import clickable_images

from digiprod_gen.backend.etl.extract_fns import read_exported_data
from digiprod_gen.backend.image import conversion
from digiprod_gen.backend.image.compress import compress
from digiprod_gen.backend.image.upscale import resize_image_keep_aspect_ratio
from digiprod_gen.backend.models.common import UpscalerModel, BackgroundRemovalModel
from digiprod_gen.backend.models.export import MBAExportUploadData
from digiprod_gen.backend.models.session import SessionState
from digiprod_gen.backend.image.conversion import pil2b64_str
from digiprod_gen.frontend.tab.prod_import.utils import import_selected_product
from digiprod_gen.frontend.tab.upload.views import display_data_for_upload, upload_product


def display_products_export_dates() -> str:
    dirs = glob("export/*/")
    export_dates = [Path(dir).name for dir in dirs]
    export_dates.sort(reverse=True)
    option = st.selectbox(
        'Choose a date of export',
        export_dates)
    return option

def display_products(selected_date_str, session_state: SessionState) -> Tuple[Image.Image, MBAExportUploadData]:
    """Display all importable products
        Expect export/import directory structure:
        export/
            YYYY-MM-DD/
                <design_cat_name>/
                    HH_MM_SS/
                        design.jpeg
                        export.json
    """
    dirs = glob(f"export/{selected_date_str}/*/")
    category_names = [Path(f).name for f in dirs]
    category_tabs = st.tabs(category_names)
    clicked_indexes = {}
    mba_upload_data = {cat_name: [] for cat_name in category_names}
    for i, category_tab in enumerate(category_tabs):
        # product_cols = category_tab.columns(3)
        category_name = category_names[i]
        product_dirs = glob(f"export/{selected_date_str}/{category_name}/*/")
        images = []
        with category_tab:
            for product_i, product_dir in enumerate(product_dirs):
                try:
                    upload_data, img_pils = read_exported_data(Path(product_dir))
                    for img_pil in img_pils:
                        images.append(f"data:image/jpeg;base64,{pil2b64_str(img_pil)}")
                        mba_upload_data[category_name].append((img_pil, upload_data))
                except Exception as e:
                    logging.warning(f"Could not read data from path {product_dir}. {e}")
            clicked = clickable_images(
                images,
                titles=[f"Image #{str(i)}" for i in range(1)],
                div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
                img_style={"margin": "5px", "height": "200px"},
                key=f"clickable_image_{category_name}_{Path(product_dir).name}"
            )
            clicked_indexes[category_name] = clicked

    set1 = set(session_state.upload_data.import_data.selected_import_products.items())
    set2 = set(clicked_indexes.items())
    clicked_category_item = set2 - set1
    session_state.upload_data.import_data.selected_import_products = clicked_indexes
    # st.write(clicked_indexes)
    # st.write(clicked_category_item)

    # only change if difference noticed
    if clicked_category_item:
        # Get first category which was really changed/clicked (i.e. != -1)
        for clicked_category_tuple in iter(clicked_category_item):
            category_name = clicked_category_tuple[0]
            clicked_index = clicked_category_tuple[1]
            if clicked_index != -1:
                break

        session_state.upload_data.import_data.last_selected_cat_name = category_name
        session_state.upload_data.import_data.last_selected_index = clicked_index
        # st.write(category_name, clicked_index)
        return mba_upload_data[category_name][clicked_index]

    # return first available image if no image was clicked
    if session_state.upload_data.import_data.last_selected_cat_name in mba_upload_data:
        return mba_upload_data[session_state.upload_data.import_data.last_selected_cat_name][session_state.upload_data.import_data.last_selected_index]
    return mba_upload_data[list(mba_upload_data.keys())[0]][0]


def display_tab_import_views(session_state: SessionState):
    st.subheader("Import MBA Products")
    if st.button("Load import data"):
        selected_date_str = display_products_export_dates()
        img_pil, upload_data = display_products(selected_date_str, session_state)
        print("SELECTED",upload_data)
        display_data_for_upload(resize_image_keep_aspect_ratio(conversion.ensure_rgba(img_pil), 4000),
                            title=upload_data.product_data.title,
                            brand=upload_data.product_data.brand,
                            bullet_1=upload_data.product_data.bullets[0],
                            bullet_2=upload_data.product_data.bullets[1],
                            disable_all=True, key_suffix="import", change_session=False)
        if st.button("Import Product"):
            import_selected_product(img_pil, upload_data, session_state)
            st.rerun()

        if not session_state.status.mba_login_successful:
            st.warning("Please login with your MBA credentials (5. MBA Upload)")
        else:
            errors = []
            compress_quality = 80

            upscaler = st.selectbox(
                'Up Scaling Method',
                (UpscalerModel.GFPGAN.value, UpscalerModel.SOME_UPSCALER.value, UpscalerModel.PIL.value,
                 UpscalerModel.ULTIMATE_SD_UPSCALER.value, UpscalerModel.HIGH_RESOLUTION_CONTROLNET.value),
                key="upscaler_selectbox_import_view")

            br_method = st.selectbox(
                'Background Removal Method',
                (BackgroundRemovalModel.OPEN_CV.value, BackgroundRemovalModel.REM_BG.value,
                 BackgroundRemovalModel.EASY_REM_BG.value),
                key="br_selectbox_import_view")


            br_tolerance = session_state.config.image_gen.background_removal.tolerance
            if br_method == BackgroundRemovalModel.OPEN_CV.value:
                br_tolerance_selected = st.slider('Background Removal Pixel Tolerance', 0, 200, value=br_tolerance, step=1, key="br_tolerance_product_import")
                if br_tolerance_selected != 0:
                    br_tolerance = br_tolerance_selected

            if st.button("Upload Product", key="upload_from_import_button"):
                # import
                progress_bar = st.progress(0, text="Import product...")
                upload_data.product_data.description = session_state.upload_data.description
                import_selected_product(img_pil, upload_data, session_state)

                # upscale
                progress_bar.progress(10, text="Upscale product...")
                response = session_state.backend_caller.post(
                    f"/image/upscaling?upscaler={upscaler}&prompt={session_state.image_gen_data.image_gen_prompt_selected}",
                    img_pil=img_pil)
                image_upscaled = conversion.bytes2pil(response.content)
                progress_bar.progress(40, text="Compress product...")
                image_upscaled = compress(image_upscaled, quality=compress_quality)
                session_state.image_gen_data.image_pil_upscaled = image_upscaled

                # remove background
                progress_bar.progress(50, text="Remove background...")
                response = session_state.backend_caller.post(
                    f"/image/background_removal?br_method={br_method}&outer_pixel_range={session_state.config.image_gen.background_removal.outer_pixel_range}&tolerance={br_tolerance}",
                    img_pil=image_upscaled)
                image_pil_br = conversion.bytes2pil(response.content)
                session_state.image_gen_data.image_pil_background_removed = image_pil_br

                # save upload ready image in session
                session_state.image_gen_data.image_pil_upload_ready = conversion.ensure_rgba(
                    conversion.pil2pil_png(image_pil_br))

                # upload_data
                progress_bar.progress(60, text="Upload product...")
                errors = upload_product(session_state)
                progress_bar.progress(100, text="Upload succeeded" if len(errors) == 0 else "Upload failed")

            if len(errors) == 0 and session_state.status.product_uploaded and st.button("Publish to MBA", key="publish_from_import_button"):
                response = session_state.backend_caller.get(
                    f"/browser/upload/publish_mba_product?session_id={session_state.session_id}&proxy={session_state.crawling_request.proxy}&searchable=true"
                )
                if response.status_code == 200:
                    st.balloons()
                else:
                    st.error("Something went wrong during publishing")
