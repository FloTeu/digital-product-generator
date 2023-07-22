import time
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from PIL import Image
from typing import Optional

from digiprod_gen.backend.image.background_removal import remove_outer_pixels
from digiprod_gen.backend.image.upscale import pil_upscale, some_upscalers_upscale
from digiprod_gen.backend.data_classes.session import ImageGenData
from digiprod_gen.backend.data_classes.common import UpscalerModel


def get_image_bytes_by_user() -> bytes | None:
    st.markdown("Please use one of the example Prompts to generate an image with Midjourney. \nYou can upload the image afterwards and proceed.")
    st.subheader("Upload Image to MBA")
    image = st.file_uploader("Image:", type=["png", "jpg", "jpeg"], key="image_gen_tab")
    return image if image == None else image.getvalue()


def display_image_editor(image_pil: Image, session_image_gen_data: ImageGenData, background_removal_buffer=0) -> Image:
    """ Image Editor view contains:
        * Upscaling
        * Baclground removal

    Upscaling is performed before we do the background removal as some upscaling methods \
    can not handle 4 dimensions (transperency channel)
    """
    st.image(image_pil)
    t_start = time.time()
    image_upscaled = image_upscaling(image_pil, session_image_gen_data)
    print(f"Time elapsed for upscaling %.2f seconds" % (time.time() - t_start))
    image_pil_br: Image = image_background_removal(image_upscaled, buffer=background_removal_buffer, session_image_gen_data=session_image_gen_data)
    return image_pil_br

def image_upscaling(image_pil: Image, session_image_gen_data: ImageGenData, upscaler: UpscalerModel = UpscalerModel.SOME_UPSCALER) -> Image:
    if st.button("Upscale") and image_pil:
        if upscaler == UpscalerModel.PIL:
            image_pil_upscaled = pil_upscale(image_pil, (4500, 4500))
        if upscaler == UpscalerModel.SOME_UPSCALER:
            image_pil_upscaled = some_upscalers_upscale(image_pil)
        session_image_gen_data.image_pil_upscaled = image_pil_upscaled
        st.image(image_pil_upscaled)
        return image_pil_upscaled
    else:
        return session_image_gen_data.image_pil_upscaled

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
