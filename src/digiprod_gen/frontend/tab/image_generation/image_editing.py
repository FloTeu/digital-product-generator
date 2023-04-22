import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from PIL import Image
from typing import Optional

from digiprod_gen.backend.image.background_removal import remove_outer_pixels
from digiprod_gen.backend.image.upscale import pil_upscale
from digiprod_gen.frontend.session import read_session, write_session


def get_image_bytes_by_user() -> bytes | None:
    st.markdown("Please use one of the example Prompts to generate an image with Midjourney. \nYou can upload the image afterwards an proceed.")
    st.subheader("Upload Image to MBA")
    image = st.file_uploader("Image:", type=["png", "jpg", "jpeg"], key="tab_ig_image")
    return image if image == None else image.getvalue()


def display_image_editor(image_pil: Image) -> Image:
    st.image(image_pil)
    image_pil_br: Image = image_background_removal(image_pil)
    return image_upscaling(image_pil_br)

def image_upscaling(image_pil: Image) -> Image:
    if st.button("Upscale") and image_pil:
        image_pil_br_upscale = pil_upscale(image_pil, (4500, 5400))
        # TODO: How to handle result pil
        image_pil_br_upscale.save("test.png")
        st.image(image_pil_br_upscale)
        return image_pil_br_upscale

def image_background_removal(image_pil: Image) -> Image:
    if st.button("Remove Background"):
        st.write("Removed Background")
        image_pil_br = remove_outer_pixels(image_pil, buffer=0)
        #write_session("image_pil_br", image_pil_br)
        # TODO: How to handle result pil
        st.image(image_pil_br)
        return image_pil_br