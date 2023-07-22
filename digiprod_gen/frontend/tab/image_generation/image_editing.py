import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from PIL import Image
from typing import Optional

from digiprod_gen.backend.image.background_removal import remove_outer_pixels
from digiprod_gen.backend.image.upscale import pil_upscale
from digiprod_gen.backend.data_classes.session import ImageGenData


def get_image_bytes_by_user() -> bytes | None:
    st.markdown("Please use one of the example Prompts to generate an image with Midjourney. \nYou can upload the image afterwards and proceed.")
    st.subheader("Upload Image to MBA")
    image = st.file_uploader("Image:", type=["png", "jpg", "jpeg"], key="image_gen_tab")
    return image if image == None else image.getvalue()


def display_image_editor(image_pil: Image, session_image_gen_data: ImageGenData, background_removal_buffer=0) -> Image:
    st.image(image_pil)
    image_pil_br: Image = image_background_removal(image_pil, buffer=background_removal_buffer, session_image_gen_data=session_image_gen_data)
    return image_upscaling(image_pil_br)

def image_upscaling(image_pil: Image) -> Image:
    if st.button("Upscale") and image_pil:
        image_pil_br_upscale = pil_upscale(image_pil, (4500, 5400))
        # TODO: How to handle result pil
        image_pil_br_upscale.save("test.png")
        st.image(image_pil_br_upscale)
        return image_pil_br_upscale

def image_background_removal(image_pil: Image, buffer, session_image_gen_data: ImageGenData) -> Image:
    if st.button("Remove Background"):
        st.write("Removed Background")
        image_pil_br = remove_outer_pixels(image_pil, buffer=buffer)
        session_image_gen_data.image_pil_background_removed = image_pil_br
        # TODO: How to handle result pil
        st.image(image_pil_br)
        return image_pil_br
    else:
        return session_image_gen_data.image_pil_background_removed
