import streamlit as st
from PIL import Image
from typing import Tuple

from digiprod_gen.backend_api.image.conversion import pil2bytes_io, bytes2pil, pil2np
from digiprod_gen.backend_api.image.background_removal import simple_remove_background, rembg
from digiprod_gen.backend_api.image.upscale import pil_upscale, some_upscalers_upscale
from digiprod_gen.backend_api.image.outpainting import outpainting_with_paella
from digiprod_gen.backend_api.image.compress import jpeg_compress, png_compress
from digiprod_gen.backend_api.models.session import ImageGenData
from digiprod_gen.backend_api.models.config import DigiProdGenImageGenBrConfig
from digiprod_gen.backend_api.models.common import UpscalerModel, BackgroundRemovalModel


def set_image_pil_generated_by_user(session_image_gen_data: ImageGenData):
    image = st.file_uploader("Image:", type=["png", "jpg", "jpeg"], key="image_gen_tab", on_change=session_image_gen_data.reset_image_data)
    if image != None:
        session_image_gen_data.image_pil_generated = bytes2pil(image.getvalue())


def display_image_editor(session_image_gen_data: ImageGenData, session_br_config=DigiProdGenImageGenBrConfig) -> Image:
    """ Image Editor view contains:
        * Upscaling
        * Baclground removal

    Upscaling is performed before we do the background removal as some upscaling methods \
    can not handle 4 dimensions (transperency channel)
    """
    col1, col2, col3 = st.columns([3,1,4])
    image_element = col3.empty()

    image_outpainted = display_image_editor_outpainting(col1, col2, image_element, session_image_gen_data)

    image_upscaled = display_image_editor_upscaling(col1, col2, image_element, session_image_gen_data, compress_quality=80)
    #image_upscaled = jpeg_compress(image_upscaled, quality=70)
    #session_image_gen_data.image_pil_upscaled = image_upscaled

    image_pil_br = display_image_editor_background_removal(col1, col2, image_element, session_br_config, session_image_gen_data, compress_quality=100)

    # display image with order br > up scaled > unchanged
    display_image_pil = image_pil_br or image_upscaled or image_outpainted or session_image_gen_data.image_pil_generated
    image_element.image(display_image_pil.resize((500,500)))

    #display_image_pil.save("image-file-uncompressed.png", "PNG")
    print("Image", pil2np(display_image_pil).shape, pil2np(display_image_pil)[0][0])

    is_download_visible = col1.checkbox("Activate Download Image Button")
    print("is_download_visible", is_download_visible)
    if is_download_visible:
        with st.spinner("Load Download Button"):
            col1.download_button("Download Image", data=pil2bytes_io(display_image_pil), file_name="export.png", mime='image/png', use_container_width=True)

    return image_pil_br or image_upscaled



def display_image_editor_outpainting(col1, col2, image_element, session_image_gen_data: ImageGenData):
    if col1.button("Outpainting", use_container_width=True):
        if session_image_gen_data.image_pil_generated and session_image_gen_data.image_gen_prompt_selected:
            with image_element, st.spinner("Outpainting..."):
                image_outpainted = image_outpainting(session_image_gen_data.image_pil_generated,
                                                     session_image_gen_data.image_gen_prompt_selected,
                                                     session_image_gen_data, output_relativ_size=(1.5, 1.5))
        else:
            st.warning("Either no image provided or the image generation prompt was not yet selected")
            image_outpainted = None
    else:
        image_outpainted = session_image_gen_data.image_pil_outpainted

    # User interaction to remove image editing again
    if image_outpainted:
        button_placeholder = col2.empty()
        if col2.button(":x:", key="remove_image_editing_outpainting_button"):
            image_outpainted = None
            session_image_gen_data.image_pil_outpainted = None
            button_placeholder.empty()
    else:
        display_button_placeholder(col2)
    return image_outpainted


def display_image_editor_upscaling(col1, col2, image_element, session_image_gen_data: ImageGenData, compress_quality: int=100):
    upscaler_method = col1.selectbox(
        'Up Scaling Method',
        (UpscalerModel.PIL.value, UpscalerModel.SOME_UPSCALER.value))
    if col1.button("Upscale", key="upscaling_button",
                   use_container_width=True) and session_image_gen_data.image_pil_generated and not session_image_gen_data.image_pil_upscaled:
        with image_element, st.spinner("Upscaling..."):
            image_to_upscale = session_image_gen_data.image_pil_outpainted or session_image_gen_data.image_pil_generated
            image_upscaled = image_upscaling(image_to_upscale, upscaler=upscaler_method)
            if compress_quality < 100:
                image_upscaled = jpeg_compress(image_upscaled, quality=compress_quality)
            session_image_gen_data.image_pil_upscaled = image_upscaled
    else:
        image_upscaled = session_image_gen_data.image_pil_upscaled

    # User interaction to remove image editing again
    if image_upscaled:
        col2.markdown("#")
        col2.markdown("###")
        col2.markdown("###")
        button_placeholder = col2.empty()
        if button_placeholder.button(":x:", key="remove_image_editing_upscaling_button"):
            image_upscaled = None
            session_image_gen_data.image_pil_upscaled = None
            button_placeholder.empty()
    else:
        col2.markdown("#")
        col2.markdown("###")
        col2.markdown("###")
        display_button_placeholder(col2)

    return image_upscaled


def display_image_editor_background_removal(col1, col2, image_element, session_br_config: DigiProdGenImageGenBrConfig,
                                            session_image_gen_data: ImageGenData, compress_quality: int = 100):
    image_upscaled = session_image_gen_data.image_pil_upscaled
    br_method = col1.selectbox(
        'Background Removal Method',
        (BackgroundRemovalModel.OPEN_CV.value, BackgroundRemovalModel.REM_BG.value))
    if col1.button("Remove Background", key="remove_background_button", use_container_width=True) and image_upscaled and not session_image_gen_data.image_pil_background_removed:
        with image_element, st.spinner("Background Removal..."):
            image_pil_br: Image = image_background_removal(image_upscaled,
                                                           br_method=br_method,
                                                           outer_pixel_range=session_br_config.outer_pixel_range,
                                                           tolerance=session_br_config.tolerance
                                                           )
            if compress_quality < 100:
                image_pil_br = png_compress(image_pil_br, quality=compress_quality)
            session_image_gen_data.image_pil_background_removed = image_pil_br
    else:
        image_pil_br = session_image_gen_data.image_pil_background_removed

    # User interaction to remove image editing again
    if image_pil_br:
        col2.markdown("#")
        col2.markdown("###")
        col2.markdown("###")
        button_placeholder = col2.empty()
        if button_placeholder.button(":x:", key="remove_image_editing_br_button"):
            image_pil_br = None
            session_image_gen_data.image_pil_background_removed = None
            button_placeholder.empty()
    else:
        col2.markdown("#")
        col2.markdown("###")
        col2.markdown("###")
        display_button_placeholder(col2)

    return image_pil_br

def image_upscaling(image_pil: Image, upscaler: UpscalerModel = UpscalerModel.SOME_UPSCALER) -> Image:
    if upscaler == UpscalerModel.PIL:
        image_pil_upscaled = pil_upscale(image_pil, (4500, 4500))
        # increase resolution after simple upscale
        # image_pil_upscaled = real_esrgan_resolution(image_pil_upscaled)
    elif upscaler == UpscalerModel.SOME_UPSCALER:
        image_pil_upscaled = some_upscalers_upscale(image_pil)
    else:
        raise NotImplementedError
    return image_pil_upscaled

def image_background_removal(image_pil: Image, br_method: BackgroundRemovalModel=BackgroundRemovalModel.OPEN_CV, **br_kwargs) -> Image:
    if br_method == BackgroundRemovalModel.OPEN_CV:
        image_pil_br = simple_remove_background(image_pil, **br_kwargs)
    elif br_method == BackgroundRemovalModel.REM_BG:
        image_pil_br = rembg(image_pil)
    else:
        raise NotImplementedError
    return image_pil_br

def image_outpainting(image_pil: Image, prompt: str, session_image_gen_data: ImageGenData, output_relativ_size: Tuple[float, float] = (1.5, 1.5)) -> Image:
    image_pil_outpainted = outpainting_with_paella(image_pil, prompt, output_relativ_size=output_relativ_size)
    session_image_gen_data.image_pil_outpainted = image_pil_outpainted
    return image_pil_outpainted

def display_button_placeholder(st_element):
    st_element.markdown("###")
    st_element.markdown("####")