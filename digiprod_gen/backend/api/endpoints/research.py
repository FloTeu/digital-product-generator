import sys
import logging
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel, Field
from llm_prompting_gen.output_parser.pydantic_parser import PydanticOutputParser
from digiprod_gen.backend.image.lvm_fns import get_gpt4_vision_response
from llm_prompting_gen.models.prompt_engineering import PromptEngineeringMessages
from llm_prompting_gen.generators import PromptEngineeringGenerator, ParsablePromptEngineeringGenerator
from langchain_community.chat_models import ChatOpenAI
from digiprod_gen.backend.image import conversion
from digiprod_gen.backend.models.request import SelectProductRequest, MBAProductsRequest, SelectListingsByImageRequest
from digiprod_gen.backend.models.response import SelectListingsByImageResponse
from digiprod_gen.frontend.tab.crawling.views import mba_products_overview_html_str
import imgkit

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("BackendAPI")

router = APIRouter()


@router.post("/select_products")
async def post_select_mba_products(request: MBAProductsRequest) -> List[str]:
    """
    Gets ~48 mba products with design and product text information.
    Via LVM (e.g. GPT-4V) three suitable products are selected (based on PoD sell expectations)
    Another LLM (e.g. GPT-35) translates the first LVM output to a list of asins.

    returns: List of product asins
    """
    mba_products = request.mba_products
    id2asin_dict = {id: prod.asin for id, prod in enumerate(mba_products)}
    products_html = mba_products_overview_html_str(mba_products, columns=8)
    img_bytes = imgkit.from_string(products_html, False, options={
        'zoom': 4,
        'quality': 100
    })
    img_pil = conversion.bytes2pil(img_bytes)

    body = SelectProductRequest(img_b64_str=conversion.pil2b64_str(img_pil), id2asin=id2asin_dict)
    return await post_select_mba_products_by_image(body)

@router.post("/select_products_by_image")
async def post_select_mba_products_by_image(request: SelectProductRequest) -> List[str]:
    """
    Gets an image with ~48 products showing designs and product texts
    Via LVM (e.g. GPT-4V) three suitable products are selected (based on PoD sell expectations)
    Another LLM (e.g. GPT-35) translates the first LVM output to a list of asins.

    returns: List of product asins
    """
    # decode base64string
    img_pil = conversion.b64_str2pil(request.img_b64_str)
    pe_msg = PromptEngineeringMessages.from_yaml("templates/research_product_selection.yaml")
    prompt = pe_msg.messages["instruction"].format().content
    lvm_suggestion = get_gpt4_vision_response(img_pil, prompt, temperature=0.0)

    llm = ChatOpenAI(temperature=0.0)
    class Asins(BaseModel):
        asins: List[str] = Field(description="List of asins")
    pe_gen = ParsablePromptEngineeringGenerator.from_json("templates/research_asin_translater.json", llm=llm, pydantic_cls=Asins)
    asins = pe_gen.generate(ai_answer=lvm_suggestion, id2asin_dict=request.id2asin)
    return asins.asins

@router.post("/select_listing_by_image")
async def post_select_listing_by_image(request: SelectListingsByImageRequest) -> SelectListingsByImageResponse:
    """
    Gets a mba product AI generated image with listing suggestions
    Via LVM (e.g. GPT-4V) the best suitable suggestions for this image are chosen.

    returns: SelectListingsByImageResponse
    """
    # decode base64string
    img_pil = conversion.b64_str2pil(request.img_b64_str)
    pe_msg = PromptEngineeringMessages.from_yaml("templates/research_listing_selection.yaml")
    prompt = pe_msg.messages["instruction"].format(**request.model_dump()).content
    output_parser = PydanticOutputParser(pydantic_object=SelectListingsByImageResponse)
    format_instruction = output_parser.get_format_instructions()
    lvm_suggestion = get_gpt4_vision_response(img_pil, prompt + format_instruction, temperature=0.0)
    return output_parser.parse(lvm_suggestion)