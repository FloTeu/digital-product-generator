import streamlit as st

from PIL import Image
from digiprod_gen.backend.models.session import ImageGenData
from digiprod_gen.backend.models.common import ImageGenerationModel
from digiprod_gen.backend.image import generation

def update_session_selected_prompt(session_image_gen_data: ImageGenData, image_gen_prompt=None):
    session_image_gen_data.image_gen_prompt_selected = image_gen_prompt if image_gen_prompt else st.session_state["image_gen_prompt"]

def display_image_generation_prompt(session_image_gen_data: ImageGenData):
    image_gen_prompt = "" if len(session_image_gen_data.image_gen_prompts) == 0 else session_image_gen_data.image_gen_prompts[0]
    st.text_area("Image Generation Prompt", value=image_gen_prompt, on_change=update_session_selected_prompt, args=(session_image_gen_data,), key="image_gen_prompt")
    # cold start
    if session_image_gen_data.image_gen_prompt_selected == None and image_gen_prompt != "":
        update_session_selected_prompt(session_image_gen_data, image_gen_prompt)

def display_image_generator(session_image_gen_data: ImageGenData) -> Image:
    image_gen_model = st.selectbox(
        'Image Generation Model',
        (ImageGenerationModel.STABLE_DIFFUSION.value, ImageGenerationModel.STABLE_DIFFUSION_SHIRT.value, ImageGenerationModel.STABLE_DIFFUSION_BARBIE.value, ImageGenerationModel.OPENJOURNEY.value, ImageGenerationModel.DEEPFLOYD_IF.value, ImageGenerationModel.POKEMON.value, ImageGenerationModel.WAIFU_DIFFUSION.value))
    if st.button("Generate Image"):
        with st.spinner('Generating image...'):
            session_image_gen_data.image_pil_generated = text2image(session_image_gen_data.image_gen_prompt_selected, image_gen_model)
            session_image_gen_data.reset_image_data()

def text2image(text: str, image_gen_model: ImageGenerationModel) -> Image:
    if image_gen_model == ImageGenerationModel.DEEPFLOYD_IF:
        return generation.generate_with_deepfloyd_if(text)
    if image_gen_model == ImageGenerationModel.STABLE_DIFFUSION_BARBIE:
        return generation.generate_with_stable_diffusion_xl_barbie(text)
    if image_gen_model == ImageGenerationModel.STABLE_DIFFUSION_SHIRT:
        return generation.generate_with_stable_diffusion_xl_shirt(text)
    elif image_gen_model == ImageGenerationModel.OPENJOURNEY:
        return generation.generate_with_openjourney(text)
    elif image_gen_model == ImageGenerationModel.STABLE_DIFFUSION:
        return generation.generate_with_stable_diffusion(text)
    elif image_gen_model == ImageGenerationModel.POKEMON:
        return generation.generate_with_pokemon(text)
    elif image_gen_model == ImageGenerationModel.WAIFU_DIFFUSION:
        return generation.generate_with_waifu(text)
    else:
        raise NotImplementedError


