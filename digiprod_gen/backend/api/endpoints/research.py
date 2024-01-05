import base64
import sys
import logging
from typing import List

from fastapi import APIRouter

from digiprod_gen.backend.browser.parser import mba as mba_parser
from digiprod_gen.backend.models.mba import MBAProduct
from digiprod_gen.backend.image import conversion

from digiprod_gen.backend.models.request import SelectProductRequest

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("BackendAPI")

router = APIRouter()


@router.post("/select_products")
async def post_select_mba_products(request: SelectProductRequest) -> List[str]:
    """
    Gets an image with ~48 products showing designs and product texts
    Via LVM (e.g. GPT-4V) three suitable products are selected (based on PoD sell expectations)
    Another LLM (e.g. GPT-35) translates the first LVM output to a list of asins.

    returns: List of product asins
    """
    # decode base64string
    img_pil = conversion.b64_str2pil(request.img_b64_str)
    from digiprod_gen.backend.image.lvm_fns import get_gpt4_vision_response
    from llm_prompting_gen.models.prompt_engineering import PromptEngineeringMessages
    from llm_prompting_gen.generators import PromptEngineeringGenerator
    from langchain.chat_models import ChatOpenAI
    pe_msg = PromptEngineeringMessages.from_json("templates/research_product_selection.json")
    prompt = pe_msg.messages["instruction"].format().content
    lvm_suggestion = get_gpt4_vision_response(img_pil, prompt)

    llm = ChatOpenAI(temperature=0.0)
    pe_gen = PromptEngineeringGenerator.from_json("templates/research_asin_translater.json", llm=llm)
    asins = pe_gen.generate(ai_answer=lvm_suggestion, id2asin_dict=request.id2asin).split(",")
    return asins

