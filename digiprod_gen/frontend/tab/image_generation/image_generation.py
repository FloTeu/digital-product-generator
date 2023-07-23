import requests
import streamlit as st
import replicate

from PIL import Image
from digiprod_gen.backend.data_classes.session import ImageGenData
from digiprod_gen.backend.data_classes.common import ImageGenerationModel
from digiprod_gen.backend.image import generation

def update_session_selected_prompt(session_image_gen_data: ImageGenData):
    session_image_gen_data.image_gen_prompt_selected = st.session_state["image_gen_prompt"]

def display_image_generation_prompt(session_image_gen_data: ImageGenData):
    image_gen_prompt = "" if len(session_image_gen_data.image_gen_prompts) == 0 else session_image_gen_data.image_gen_prompts[0]
    st.text_area("Image Generation Prompt", value=image_gen_prompt, on_change=update_session_selected_prompt, args=(session_image_gen_data,), key="image_gen_prompt")
    # cold start
    if session_image_gen_data.image_gen_prompt_selected == None:
        update_session_selected_prompt(session_image_gen_data)

def display_image_generator(session_image_gen_data: ImageGenData) -> Image:
    image_gen_model = st.selectbox(
        'What is you preferred image generation model?',
        (ImageGenerationModel.OPENJOURNEY.value, ImageGenerationModel.STABLE_DIFFUSION.value, ImageGenerationModel.DEEPFLOYD_IF.value, ImageGenerationModel.POKEMON.value, ImageGenerationModel.WAIFU_DIFFUSION.value))
    if st.button("Generate Image"):
        session_image_gen_data.image_pil_generated = text2image(session_image_gen_data.image_gen_prompt_selected, image_gen_model)
        session_image_gen_data.reset_image_data()

def text2image(text: str, image_gen_model: ImageGenerationModel) -> Image:
    if image_gen_model == ImageGenerationModel.DEEPFLOYD_IF:
        return generation.generate_with_deepfloyd_if(text)
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


