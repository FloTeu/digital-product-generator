import time
import streamlit as st
from PIL import Image

from digiprod_gen.backend.image.conversion import pil2bytes_io, bytes2pil
from digiprod_gen.backend.image.background_removal import remove_outer_pixels, rembg
from digiprod_gen.backend.image.upscale import pil_upscale, some_upscalers_upscale
from digiprod_gen.backend.data_classes.session import ImageGenData
from digiprod_gen.backend.data_classes.common import UpscalerModel, BackgroundRemovalModel


def set_image_pil_generated_by_user(session_image_gen_data: ImageGenData):
    image = st.file_uploader("Image:", type=["png", "jpg", "jpeg"], key="image_gen_tab", on_change=session_image_gen_data.reset_image_data)
    if image != None:
        session_image_gen_data.image_pil_generated = bytes2pil(image.getvalue())


def display_image_editor(session_image_gen_data: ImageGenData, background_removal_buffer=0) -> Image:
    """ Image Editor view contains:
        * Upscaling
        * Baclground removal

    Upscaling is performed before we do the background removal as some upscaling methods \
    can not handle 4 dimensions (transperency channel)
    """
    col1, col2 = st.columns(2)
    image_element = col2.empty()

    t_start = time.time()
    upscaler_method = col1.selectbox(
        'What is you preferred up scaling method?',
        (UpscalerModel.PIL.value, UpscalerModel.SOME_UPSCALER.value))
    if col1.button("Upscale") and session_image_gen_data.image_pil_generated:
        with image_element, st.spinner("Upscaling..."):
            image_upscaled = image_upscaling(session_image_gen_data.image_pil_generated, session_image_gen_data, upscaler=upscaler_method)
    else:
        image_upscaled = session_image_gen_data.image_pil_upscaled
    print(f"Time elapsed for upscaling %.2f seconds" % (time.time() - t_start))

    br_method = col1.selectbox(
        'What is you preferred background removal method?',
        (BackgroundRemovalModel.OPEN_CV.value, BackgroundRemovalModel.REM_BG.value))
    if col1.button("Remove Background") and image_upscaled:
        with image_element, st.spinner("Background Removal..."):
            image_pil_br: Image = image_background_removal(image_upscaled, buffer=background_removal_buffer, session_image_gen_data=session_image_gen_data, br_method=br_method)
    else:
        image_pil_br = session_image_gen_data.image_pil_background_removed
    # display image with order br > up scaled > unchanged
    display_image_pil = image_pil_br or image_upscaled or session_image_gen_data.image_pil_generated
    image_element.image(display_image_pil)

    col1.download_button("Download Image", data=pil2bytes_io(display_image_pil), file_name="export.png", mime='image/png')

    return image_pil_br or image_upscaled

def image_upscaling(image_pil: Image, session_image_gen_data: ImageGenData, upscaler: UpscalerModel = UpscalerModel.SOME_UPSCALER) -> Image:
    if upscaler == UpscalerModel.PIL:
        image_pil_upscaled = pil_upscale(image_pil, (4500, 4500))
    elif upscaler == UpscalerModel.SOME_UPSCALER:
        image_pil_upscaled = some_upscalers_upscale(image_pil)
    else:
        raise NotImplementedError
    session_image_gen_data.image_pil_upscaled = image_pil_upscaled
    return image_pil_upscaled

def image_background_removal(image_pil: Image, buffer, session_image_gen_data: ImageGenData, br_method: BackgroundRemovalModel=BackgroundRemovalModel.OPEN_CV) -> Image:
    if br_method == BackgroundRemovalModel.OPEN_CV:
        image_pil_br = remove_outer_pixels(image_pil, buffer=buffer)
    elif br_method == BackgroundRemovalModel.REM_BG:
        image_pil_br = rembg(image_pil)
    else:
        raise NotImplementedError
    session_image_gen_data.image_pil_background_removed = image_pil_br
    return image_pil_br