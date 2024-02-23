import logging
import uuid

import streamlit as st
from os import listdir, getcwd
from typing import Tuple
from pathlib import Path
from glob import glob
from PIL import Image
from st_clickable_images import clickable_images

from digiprod_gen.backend.etl.extract_fns import read_exported_data
from digiprod_gen.backend.models.export import MBAExportUploadData
from digiprod_gen.backend.models.session import SessionState
from digiprod_gen.backend.image.conversion import pil2b64_str


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
                    img_pil, upload_data = read_exported_data(Path(product_dir))
                    images.append(f"data:image/jpeg;base64,{pil2b64_str(img_pil)}")
                    mba_upload_data[category_name].append((img_pil, upload_data))
                except Exception as e:
                    logging.warning(f"Could not read data from path {product_dir}. {e}")
                # product_col = product_cols[product_i % 3]
                # with product_col:
                #     st.image(img_pil)
                #     st.write(upload_data.product_data.title)
                    #images.append(f"data:image/jpeg;base64,{pil2b64_str(img_pil)}")
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
