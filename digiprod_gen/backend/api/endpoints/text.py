from typing import List
from fastapi import APIRouter, UploadFile, File
from langchain.chat_models import ChatOpenAI
from llm_prompting_gen.generators import PromptEngineeringGenerator, ParsablePromptEngineeringGenerator

from digiprod_gen.backend.prompt_engineering.utils import extract_list_from_output
from digiprod_gen.backend.models.mba import MBAProduct, MBAProductTextType
from digiprod_gen.backend.models.request import KeywordExtractionRequest, ListingGenRequest
from digiprod_gen.backend.text.text_gen_fns import mba_products2llm_prompt_gen_input, get_product_text_gen, remove_banned_words_from_list
from digiprod_gen.backend.text.mba_banned_word import MBA_BANNED_WORDS

router = APIRouter()

@router.post("/gen/prompts")
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


@router.post("/extract/keywords")
async def get_keywords(kw_request: KeywordExtractionRequest,
                       temperature: float=0.7) -> List[str]:
    """
    Creates a list of keywords via the power of Large Language Models.
    As input a text is required.
    """
    llm = ChatOpenAI(temperature=temperature)
    keyword_extractor = PromptEngineeringGenerator.from_json("templates/product_keyword_extractor.json", llm=llm)
    keyword_list = keyword_extractor.generate(text=kw_request.text).split(",")
    if kw_request.remove_banned_words:
        return [k for k in keyword_list if k.lower().strip() not in MBA_BANNED_WORDS]
    else:
        return keyword_list

@router.post("/gen/listings")
async def gen_listings(lg_request: ListingGenRequest,
                        temperature: float=0.7) -> List[str]:
    """
    Creates a list of listings (i.e. title, brand or bullet points) via the power of Large Language Models.
    As input a text a list of mba_products is required.
    """
    llm = ChatOpenAI(temperature=temperature)
    product_listing_gen: ParsablePromptEngineeringGenerator = get_product_text_gen(llm, lg_request.mba_products, lg_request.type)
    predicted_listings: List[str] = extract_list_from_output(
        product_listing_gen.generate(keywords=lg_request.keywords))
    if lg_request.remove_banned_words:
        return remove_banned_words_from_list(predicted_listings, MBA_BANNED_WORDS)
    else:
        return predicted_listings