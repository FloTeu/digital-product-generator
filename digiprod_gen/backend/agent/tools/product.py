import random
import requests
import json
from datetime import datetime
from typing import List, Dict
from pydantic.json import pydantic_encoder

from langchain_core.tools import tool

from digiprod_gen.backend.agent.models.api import MBAProductsRequest
from digiprod_gen.backend.agent.models.memory import MemoryId, MemoryAddResponse
from digiprod_gen.backend.api.common import CONFIG
from digiprod_gen.backend.models.mba import MBAProduct
from digiprod_gen.backend.models.response import ImageCheckResponse
from digiprod_gen.backend.models.common import ImageCaptioningModel, ImageGenerationModel
from digiprod_gen.backend.image.crop import get_mba_design_crop
from digiprod_gen.backend.image import conversion
from digiprod_gen.backend.agent.memory import global_memory_container
from digiprod_gen.frontend.backend_caller import BackendCaller


@tool("randomselectMbaProductsTool")
def select_random_mba_products(output_size: int = 4) -> Dict[str, MemoryAddResponse]:
    """use to select a subsample of mba products for further product generation"""
    if MemoryId.MBA_PRODUCTS not in global_memory_container:
        return {"response": "Failure. No mba products crawled yet"}
    mba_products = global_memory_container[MemoryId.MBA_PRODUCTS]
    mba_products_selected = random.choices(mba_products,k=output_size)
    global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS] = mba_products_selected
    return {"response": MemoryAddResponse(uuid=MemoryId.SELECTED_MBA_PRODUCTS)}

@tool("printMbaProductsTool")
def print_select_mba_products():
    """use to print the selected mba products"""
    mba_products = global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS]
    for mba_product in mba_products:
        print(mba_product.json())
    return {"response": "Successfully printed mba products"}

@tool("selectMBAProductsTool")
def select_mba_products() -> Dict[str, MemoryAddResponse]:
    """
    Takes all crawled mba products and creates chooses the best suitable products
    for further processing via AI technology.
    """
    mba_products = global_memory_container[MemoryId.MBA_PRODUCTS]

    request = MBAProductsRequest(mba_products=mba_products)
    backend_caller = BackendCaller(CONFIG.backend)
    try:
        response = backend_caller.post(f"/research/select_products",
                                                     json=request.dict())
    except Exception as e:
        return {"response": "Failure"}


    global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS] = response.json()
    return {"response": MemoryAddResponse(uuid=MemoryId.SELECTED_MBA_PRODUCTS)}

@tool("enrichMBAProductsWithImageCaptionTool")
def enrich_mba_products_with_image_caption(
                    caption_model: ImageCaptioningModel = ImageCaptioningModel.GPT4
                    ) -> Dict[str, MemoryAddResponse]:
    """
    Takes s subsample of crawled mba products and adds the image_prompt attribute.
    """
    if MemoryId.SELECTED_MBA_PRODUCTS not in global_memory_container:
        return {"response": "Failure. No mba products selected yet"}
    mba_products = global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS]
    backend_caller = BackendCaller(CONFIG.backend)

    def get_image_caption(mba_product: MBAProduct) -> str:
        image_pil = conversion.bytes2pil(requests.get(mba_product.image_url, stream=True).content)
        image_pil_croped = get_mba_design_crop(image_pil)
        response = backend_caller.post(f"/image/caption?caption_model={caption_model}",
                                       img_pil=image_pil_croped)
        return response.json()

    def get_text_caption(mba_product: MBAProduct) -> str:
        image_pil = conversion.bytes2pil(requests.get(mba_product.image_url, stream=True).content)
        image_pil_croped = get_mba_design_crop(image_pil)
        response = backend_caller.post(f"/image/caption?extract_text_caption=true",
                                                             img_pil=image_pil_croped)
        return response.json()

    mba_products_with_caption: List[MBAProduct] = []
    for mba_product in mba_products:
        mba_product.image_prompt = get_image_caption(mba_product)
        mba_product.image_text_caption = get_text_caption(mba_product)
        mba_products_with_caption.append(mba_product)

    global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS] = mba_products_with_caption
    return {"response": MemoryAddResponse(uuid=MemoryId.SELECTED_MBA_PRODUCTS)}



@tool("getPromptSuggestionsTool")
def get_prompt_suggestions(
                    ) -> Dict[str, List[str]]:
    """
    Returns text-to-image prompts for provided mba_products
    """
    mba_products = global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS]

    backend_caller = BackendCaller(CONFIG.backend)
    json_data = json.dumps(mba_products, default=pydantic_encoder)

    response = backend_caller.post(f"/text/gen/prompts",
                                   data=json_data)
    return {"response": response.json()}

@tool("generateImageTool")
def generate_image(
                    search_term: str,
                    prompt: str,
                    image_gen_model: ImageGenerationModel = ImageGenerationModel.DALLE_3
                    ) -> Dict[str, bytes]:
    """
    Generates an ai image and stores it into memory
    """
    backend_caller = BackendCaller(CONFIG.backend)
    response = backend_caller.get(f"/image/generation?prompt={prompt}&image_gen_model={image_gen_model}")
    if response.status_code != 200:
        return {"response": "Failure"}
    image_pil_generated = conversion.bytes2pil(response.content)
    image_pil_generated.save(f"export/{search_term}_{str(datetime.now())}.png")
    global_memory_container[MemoryId.IMAGE_RAW] = image_pil_generated

    return {"response": MemoryAddResponse(uuid=MemoryId.IMAGE_RAW, success=True)}

@tool("evaluateImageTool")
def evaluate_image(
                    uuid: str,
                    prompt: str
                    ) -> Dict[str, Dict[str, ImageCheckResponse]]:
    """
    Checks whether image is suitable for a print on demand design.
    """
    img_pil = global_memory_container[uuid]
    backend_caller = BackendCaller(CONFIG.backend)
    response = backend_caller.post(f"/image/check?prompt={prompt}", img_pil=img_pil)
    if response.status_code != 200:
        return {"response": "Failure"}
    return {"response": response.json()}

