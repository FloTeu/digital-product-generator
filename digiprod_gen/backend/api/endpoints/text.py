from typing import List
from fastapi import APIRouter, UploadFile, File
from langchain.chat_models import ChatOpenAI
from llm_prompting_gen.generators import PromptEngineeringGenerator

from digiprod_gen.backend.prompt_engineering.utils import extract_list_from_output
from digiprod_gen.backend.models.mba import MBAProduct
from digiprod_gen.backend.models.request import KeywordExtractionRequest
from digiprod_gen.backend.text.text_gen_fns import mba_products2llm_prompt_gen_input

router = APIRouter()

@router.post("/prompt_gen")
async def get_prompt_suggestions(mba_products: List[MBAProduct],
                            temperature: float=0.7) -> List[str]:
    """
    Creates a list of text-to-image prompts via the power of Large Language Models.
    As input a list of few shot examples is required.
    """
    llm = ChatOpenAI(temperature=temperature)
    prompt_gen = PromptEngineeringGenerator.from_json("templates/stable_diffusion_prompt_gen.json", llm)
    llm_prompt_gen_input = mba_products2llm_prompt_gen_input(mba_products)
    llm_output = prompt_gen.generate(text=llm_prompt_gen_input)
    return extract_list_from_output(llm_output)


@router.post("/keywords")
async def get_keywords(kw_request: KeywordExtractionRequest,
                       temperature: float=0.7) -> List[str]:
    """
    Creates a list of keywords via the power of Large Language Models.
    As input a text is required.
    """
    llm = ChatOpenAI(temperature=temperature)
    keyword_extractor = PromptEngineeringGenerator.from_json("templates/product_keyword_extractor.json", llm=llm)
    return keyword_extractor.generate(text=kw_request.text).split(",")