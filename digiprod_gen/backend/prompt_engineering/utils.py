from typing import List
from digiprod_gen.backend.prompt_engineering import midjourney_prompt_examples
from digiprod_gen.backend.data_classes.common import MBAMidjourneyOutputModel
def get_midjourney_example_prompts() -> List[str]:
    return [midjourney.__dict__[item] for item in dir(midjourney) if item.startswith("prompt_example")]

def enhance_midjourney_prompts(prompts: List[str], aspect="5:6"):
    """

    :return:
    """

    return

def extract_list_from_output(llm_output) -> List[str]:
    """Gets an LLM output string and tries to extract multiple elements as list"""

    # If gpt recommends multiple prompts, try to extract them
    number_indicator = [str(i) for i in range(10)]
    prompts = [p.replace("Prompt", "")[3:].strip('"').strip(':') for p in llm_output.split("\n") if p[0:1] in number_indicator]
    return prompts if len(prompts) > 0 else [llm_output]
