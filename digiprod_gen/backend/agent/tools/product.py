import random
import requests
import json
from typing import List, Dict

from langchain_core.tools import tool

from digiprod_gen.backend.agent.models.api import MBAProductsRequest
from digiprod_gen.backend.agent.models.io import MBAProductIDs, MBAProductUrls
from digiprod_gen.backend.api.common import CONFIG
from digiprod_gen.backend.models.mba import MBAProduct
from digiprod_gen.backend.models.common import ImageCaptioningModel, ImageGenerationModel
from digiprod_gen.backend.image.crop import get_mba_design_crop
from digiprod_gen.backend.image import conversion
from digiprod_gen.frontend.backend_caller import BackendCaller


@tool("randomselectMbaProductsTool", args_schema=MBAProductIDs)
def select_random_mba_products(mba_product_ids: List[str], max_output: int = 4) -> Dict[str, List[MBAProduct]]:
    """use to select a subsample of mba products for further product generation"""
    # Selects a subsample of suitable mba_products to create new products
    return {"response": random.sample(mba_product_ids, k=min(random.randint(1,max_output), len(mba_product_ids)))}


@tool("printMbaProductsTool", args_schema=MBAProductsRequest)
def print_select_mba_products(mba_products: List[MBAProduct]):
    """use to print the selected mba products"""
    for mba_product in mba_products:
        print(MBAProduct(**mba_product).json())
    return {"response": "Successfully printed mba products"}


@tool("selectMBAProductsTool", args_schema=MBAProductsRequest)
def select_mba_products(mba_products: List[MBAProduct]) -> Dict[str, List[MBAProduct]]:
    """
    Takes all crawled mba products and creates chooses the best suitable products
    for further processing via AI technology.
    """

    request = MBAProductsRequest(mba_products=mba_products)
    backend_caller = BackendCaller(CONFIG.backend)
    try:
        response = backend_caller.post(f"/research/select_products",
                                                     json=request.dict())
    except Exception as e:
        return {"response": "Failure"}
    return {"response": response.json()}

@tool("enrichMBAProductsWithImageCaptionTool", args_schema=MBAProductsRequest)
def enrich_mba_products_with_image_caption(mba_products: List[MBAProduct],
                    caption_model: ImageCaptioningModel = ImageCaptioningModel.GPT4
                    ) -> Dict[str, List[MBAProduct]]:
    """
    Takes s subsample of crawled mba products and adds the image_prompt attribute.
    """

    def get_image_caption(mba_product: MBAProduct) -> str:
        image_pil = conversion.bytes2pil(requests.get(mba_product.image_url, stream=True).content)
        image_pil_croped = get_mba_design_crop(image_pil)
        backend_caller = BackendCaller(CONFIG.backend)
        response = backend_caller.post(f"/image/caption?caption_model={caption_model}",
                                       img_pil=image_pil_croped)
        return response.json()

    mba_products_with_caption: List[MBAProduct] = []
    for mba_product in mba_products:
        mba_product = MBAProduct(**mba_product)
        mba_product.image_prompt = get_image_caption(mba_product)
        mba_products_with_caption.append(mba_product)

    return {"response": mba_products_with_caption}



@tool("getPromptSuggestionsTool", args_schema=MBAProductsRequest)
def get_prompt_suggestions(mba_products: List[MBAProduct],
                    ) -> Dict[str, List[str]]:
    """
    Returns text-to-image prompts for provided mba_products
    """
    backend_caller = BackendCaller(CONFIG.backend)
    json_data = json.dumps(mba_products)
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
    Returns text-to-image prompts for provided mba_products
    """
    backend_caller = BackendCaller(CONFIG.backend)
    response = backend_caller.post(f"/image/generation?prompt={prompt}&image_gen_model={image_gen_model}")
    bytes = response.content
    image_pil_generated = conversion.bytes2pil(bytes)
    image_pil_generated.save(f"export/{search_term}.png")

    return {"response": bytes}
