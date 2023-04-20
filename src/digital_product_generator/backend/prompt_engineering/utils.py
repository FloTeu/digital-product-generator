from typing import List
from digital_product_generator.prompt_engineering import midjourney

def get_midjourney_example_prompts() -> List[str]:
    return [midjourney.__dict__[item] for item in dir(midjourney) if item.startswith("prompt_example")]

def enhance_midjourney_prompts(prompts: List[str], aspect="5:6"):
    """

    :return:
    """

    return