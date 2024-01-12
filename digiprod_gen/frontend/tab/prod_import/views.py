import streamlit as st
from os import listdir, getcwd
from pathlib import Path
from glob import glob

from digiprod_gen.backend.etl.extract_fns import read_exported_data
from digiprod_gen.backend.models.export import MBAUploadData


def display_products_export_dates() -> str:
    dirs = glob("export/*/")
    export_dates = [Path(dir).name for dir in dirs]
    option = st.selectbox(
        'Choose a date of export',
        export_dates)
    return option

def display_products(selected_date_str) -> None:
    dirs = glob(f"export/{selected_date_str}/*/")
    category_names = [Path(f).name for f in dirs]
    category_tabs = st.tabs(category_names)
    for i, category_tab in enumerate(category_tabs):
        product_cols = category_tab.columns(3)
        category_name = category_names[i]
        product_dirs = glob(f"export/{selected_date_str}/{category_name}/*/")
        for product_i, product_dir in enumerate(product_dirs):
            img_pil, upload_data = read_exported_data(Path(product_dir))
            with category_tab:
                product_col = product_cols[product_i % 3]
                with product_col:
                    st.image(img_pil)
                    st.write(upload_data.product_data.title)
        #st.write(category_names)

