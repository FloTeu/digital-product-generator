from typing import List

from digiprod_gen.backend.models.mba import MBAProduct, MBAProductTextType
from digiprod_gen.backend.text.mba_banned_word import MBA_BANNED_WORDS
from llm_prompting_gen.generators import ParsablePromptEngineeringGenerator, PromptEngineeringGenerator


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

def remove_banned_words(example: str):
    for mba_banned_word in MBA_BANNED_WORDS:
        text_words = example.split()
        result_words = [word for word in text_words if mba_banned_word not in word.lower()]
        example = ' '.join(result_words)
    return example

def get_product_text_gen(llm, mba_products, mba_product_text_type: MBAProductTextType) -> ParsablePromptEngineeringGenerator:
    if mba_product_text_type == MBAProductTextType.BULLET:
        product_text_gen = PromptEngineeringGenerator.from_json("templates/product_text_bullet_gen.json", llm=llm)
        product_text_gen.prompt_elements.examples = [remove_banned_words(bullet) for mba_product in mba_products for bullet in mba_product.bullets]
    elif mba_product_text_type == MBAProductTextType.BRAND:
        product_text_gen = PromptEngineeringGenerator.from_json("templates/product_text_brand_gen.json", llm=llm)
        product_text_gen.prompt_elements.examples = [remove_banned_words(mba_product.brand) for mba_product in mba_products]
    elif mba_product_text_type == MBAProductTextType.TITLE:
        product_text_gen = PromptEngineeringGenerator.from_json("templates/product_text_title_gen.json", llm=llm)
        product_text_gen.prompt_elements.examples = [remove_banned_words(mba_product.title) for mba_product in mba_products]

    # Make sure output does not contain the banned words
    product_text_gen.prompt_elements.instruction = f"{product_text_gen.prompt_elements.instruction}\nDo not include any of the following words: {MBA_BANNED_WORDS} in your output."

    # # Input similar to few shot examples
    # product_text_gen.prompt_elements.input = f"Create six product {mba_product_text_type} texts in the format described above"
    return product_text_gen


def remove_banned_words_from_list(text_suggestions: List[str], banned_words):
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
