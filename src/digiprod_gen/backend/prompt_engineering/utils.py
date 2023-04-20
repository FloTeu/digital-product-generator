from typing import List
from digiprod_gen.backend.prompt_engineering import midjourney

def get_midjourney_example_prompts() -> List[str]:
    return [midjourney.__dict__[item] for item in dir(midjourney) if item.startswith("prompt_example")]

def enhance_midjourney_prompts(prompts: List[str], aspect="5:6"):
    """

    :return:
    """

    return