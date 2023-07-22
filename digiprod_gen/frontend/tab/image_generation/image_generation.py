import requests
import streamlit as st
import replicate

from PIL import Image
from digiprod_gen.backend.data_classes.session import ImageGenData
from digiprod_gen.backend.data_classes.common import ImageGenerationModel
from digiprod_gen.backend.image import generation

def display_image_generator(session_image_gen_data: ImageGenData) -> Image:
    image_gen_prompt = "" if len(session_image_gen_data.image_gen_prompts) == 0 else session_image_gen_data.image_gen_prompts[0]
    text = st.text_area("Image Generation Prompt", value=image_gen_prompt)
    image_gen_model = st.selectbox(
        'What is you preferred image generation model?',
        (ImageGenerationModel.DEEPFLOYD_IF.value, ImageGenerationModel.OPENJOURNEY.value, ImageGenerationModel.POKEMON.value))
    if st.button("Generate Image"):
        session_image_gen_data.image_pil_generated = text2image(text, image_gen_model)
        session_image_gen_data.reset_image_data()

def text2image(text: str, image_gen_model: ImageGenerationModel) -> Image:
    if image_gen_model == ImageGenerationModel.DEEPFLOYD_IF:
        return generation.generate_with_deepfloyd_if(text)
    elif image_gen_model == ImageGenerationModel.OPENJOURNEY:
        return generation.generate_with_openjourney(text)
    elif image_gen_model == ImageGenerationModel.POKEMON:
        return generation.generate_with_pokemon(text)
    else:
        raise NotImplementedError


