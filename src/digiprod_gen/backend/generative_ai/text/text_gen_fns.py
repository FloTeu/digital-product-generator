from typing import List

from digiprod_gen.backend.data_classes.mba import MBAProduct, MBAProductTextType
from digiprod_gen.backend.generative_ai.text.data_classes import MBAMidjourneyPromptGenerator, ProductTextGenerator
from mid_prompt_gen.backend.midjourney.utils import get_shirt_design_prompt_examples


def combine_bullets(products: List[MBAProduct]) -> str:
    combined_bullets = ""
    for product in products:
        if product.bullets:
            combined_bullets += ' '.join(product.bullets) + ' '
    return combined_bullets.strip()


def get_midjourney_prompt_gen(llm) -> MBAMidjourneyPromptGenerator:
    midjourney_prompt_gen = MBAMidjourneyPromptGenerator(llm)
    midjourney_prompt_gen.set_context()
    prompt_examples = get_shirt_design_prompt_examples()
    midjourney_prompt_gen.set_few_shot_examples(prompt_examples)
    return midjourney_prompt_gen


def get_product_text_gen(llm, mba_products, mba_product_text_type: MBAProductTextType, marketplace) -> ProductTextGenerator:
    product_text_gen = ProductTextGenerator(llm)
    product_text_gen.set_context()
    few_shot_examples = []
    if mba_product_text_type == MBAProductTextType.BULLET:
        for mba_product in mba_products:
            for bullet in mba_product.bullets:
                few_shot_examples.append(bullet)
    elif mba_product_text_type == MBAProductTextType.BRAND:
        for mba_product in mba_products:
            few_shot_examples.append(mba_product.brand)
    elif mba_product_text_type == MBAProductTextType.TITLE:
        for mba_product in mba_products:
            few_shot_examples.append(mba_product.title)
    product_text_gen.set_few_shot_examples(few_shot_examples, mba_product_text_type)
    product_text_gen._set_human_message(mba_product_text_type, marketplace)
    return product_text_gen


def remove_banned_words(text_suggestions: List[str], banned_words):
    result = []
    for text_suggestion in text_suggestions:
        # Split the string into words
        words = text_suggestion.split()
        # Remove banned words
        words = [word for word in words if word.lower() not in banned_words]
        # Join the words back into a string
        modified_string = ' '.join(words)
        result.append(modified_string)
    return result


def add_aspect_ration(image_gen_prompts: List[str], aspect_ratio="5:6") -> List[str]:
    image_gen_prompts_with_ar = []
    for image_gen_prompt in image_gen_prompts:
        if "--ar" not in image_gen_prompt:
            image_gen_prompt += f" --ar {aspect_ratio}"
        image_gen_prompts_with_ar.append(image_gen_prompt)
    return image_gen_prompts_with_ar
