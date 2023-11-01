from typing import List

from digiprod_gen.backend.models.mba import MBAProduct, MBAProductTextType, MBAMarketplaceDomain
from digiprod_gen.backend.text.data_classes import ProductTextGenerator


def combine_bullets(product: MBAProduct) -> str:
    return ' '.join(product.bullets) + ' ' if product.bullets else ""


def mba_products2llm_prompt_gen_input(mba_products: List[MBAProduct]) -> str:
    llm_prompt_gen_input = ""
    for i, mba_product in enumerate(mba_products):
        # Either take image captioning or (with less prio) combine product bullets
        if mba_product.image_text_caption and mba_product.image_prompt:
            llm_prompt_gen_input += f"Product {i+1} Description: {mba_product.image_prompt} Text Caption: {mba_product.image_text_caption}\n"
        else:
            llm_prompt_gen_input += combine_bullets(mba_product)
    return llm_prompt_gen_input.strip()

def get_product_text_gen(llm, mba_products, mba_product_text_type: MBAProductTextType, marketplace: MBAMarketplaceDomain) -> ProductTextGenerator:
    product_text_gen = ProductTextGenerator(llm)
    product_text_gen._set_context(mba_product_text_type)
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
    product_text_gen._set_io_prompt(mba_product_text_type, marketplace)
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
