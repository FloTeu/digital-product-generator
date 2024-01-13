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
from digiprod_gen.backend.models.mba import MBAProduct, MBAProductTextType
from digiprod_gen.backend.models.response import ImageCheckResponse, SelectListingsByImageResponse
from digiprod_gen.backend.models.request import ListingGenRequest, KeywordExtractionRequest, SelectListingsByImageRequest
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

    selected_asins = response.json()
    selected_mba_products = [mba_product for mba_product in mba_products if mba_product.asin in selected_asins]

    global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS] = selected_mba_products
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
                    ) -> Dict[str, MemoryAddResponse]:
    """
    Returns text-to-image prompts for provided mba_products
    """
    mba_products = global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS]

    backend_caller = BackendCaller(CONFIG.backend)
    json_data = json.dumps(mba_products, default=pydantic_encoder)

    response = backend_caller.post(f"/text/gen/prompts",
                                   data=json_data)
    prompt_suggestions = response.json()
    global_memory_container.status.prompts_generated = True
    global_memory_container[MemoryId.PROMPT_SUGGESTIONS] = prompt_suggestions
    return {"response": MemoryAddResponse(uuid=MemoryId.PROMPT_SUGGESTIONS, success=True, data=prompt_suggestions)}

@tool("generateImageTool")
def generate_image(
                    search_term: str,
                    prompt: str,
                    image_gen_model: ImageGenerationModel = ImageGenerationModel.DALLE_3
                    ) -> Dict[str, MemoryAddResponse]:
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
    global_memory_container[MemoryId.IMAGE_PROMPT] = prompt
    return {"response": MemoryAddResponse(uuid=MemoryId.IMAGE_RAW, success=True)}

@tool("evaluateImageTool")
def evaluate_image(
                    prompt: str
                    ) -> Dict[str, Dict[str, ImageCheckResponse]]:
    """
    Checks whether image is suitable for a print on demand design.
    """
    img_pil = global_memory_container[MemoryId.IMAGE_RAW]
    backend_caller = BackendCaller(CONFIG.backend)
    response = backend_caller.post(f"/image/check?prompt={prompt}", img_pil=img_pil)
    if response.status_code != 200:
        return {"response": "Failure"}
    return {"response": response.json()}

@tool("extractKeywords")
def extract_keywords(
                    ) -> Dict[str, MemoryAddResponse]:
    """
    Extract keywords from crawled mba products
    """
    backend_caller = BackendCaller(CONFIG.backend)

    if not global_memory_container.status.detail_pages_crawled:
        return {"response": "Failure. No mba product details crawled yet"}
    mba_products = global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS]

    keyword_text = ""
    for mba_product in mba_products:
        keyword_text += f"{mba_product.brand} {mba_product.title} {' '.join([bullet for bullet in mba_product.bullets])}\n"
    KeywordExtractionRequest(text=keyword_text)
    response = backend_caller.post(f"/text/extract/keywords", data=KeywordExtractionRequest(text=keyword_text).model_dump_json())

    if response.status_code != 200:
        return {"response": "Failure"}

    global_memory_container[MemoryId.KEYWORDS] = response.json()
    global_memory_container.status.keywords_extracted = True
    return {"response": MemoryAddResponse(uuid=MemoryId.KEYWORDS, success=True)}

@tool("generateListingSuggestions")
def generate_listing_suggestions(
        product_type: MBAProductTextType
        ) -> Dict[str, MemoryAddResponse]:
    """
    Generates listing suggestions such as title, brand or bullets
    """
    if not global_memory_container.status.keywords_extracted:
        return {"response": "Failure. No keywords extracted yet"}

    backend_caller = BackendCaller(CONFIG.backend)
    mba_products: List[MBAProduct]= global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS]
    if product_type == MBAProductTextType.BRAND:
        examples = [mba_prod.brand for mba_prod in mba_products]
        memory_id = MemoryId.BRAND_SUGGESTIONS
    elif product_type == MBAProductTextType.TITLE:
        examples = [mba_prod.title for mba_prod in mba_products]
        memory_id = MemoryId.TITLE_SUGGESTIONS
    elif product_type == MBAProductTextType.BULLET:
        examples = [bullet for mba_product in mba_products for bullet in mba_product.bullets]
        memory_id = MemoryId.BULLET_SUGGESTIONS
    else:
        raise NotImplementedError

    listing_gen_request = ListingGenRequest(type=product_type, examples=examples, keywords=",".join(global_memory_container[MemoryId.KEYWORDS]))
    response = backend_caller.post(f"/text/gen/listings", data=listing_gen_request.model_dump_json())
    if response.status_code != 200:
        return {"response": "Failure"}

    listing_suggestion = response.json()
    global_memory_container[memory_id] = listing_suggestion
    if all([product_type_i in global_memory_container for product_type_i in [MBAProductTextType.BRAND, MBAProductTextType.TITLE, MBAProductTextType.BULLET]]):
        global_memory_container.status.listing_generated = True

    return {"response": MemoryAddResponse(uuid=memory_id, success=True, data=None)}


@tool("selectMBAListingsTool")
def select_mba_listings() -> Dict[str, SelectListingsByImageResponse]:
    """
    Takes ai generated mba product image and listing suggestions and decides which
    listing suggestion (i.e. title, brand, bullets) is the best suitable for the image.
    """
    if not global_memory_container.status.listing_generated:
        return {"response": "Failure. No listings generated yet"}
    title_suggestions = global_memory_container[MemoryId.TITLE_SUGGESTIONS]
    brand_suggestions = global_memory_container[MemoryId.BRAND_SUGGESTIONS]
    bullet_suggestions = global_memory_container[MemoryId.BULLET_SUGGESTIONS]
    img_pil = global_memory_container[MemoryId.IMAGE_RAW]

    request = SelectListingsByImageRequest(img_b64_str=conversion.pil2b64_str(img_pil),
                                           title_suggestions=title_suggestions,
                                           brand_suggestions=brand_suggestions,
                                           bullet_suggestions=bullet_suggestions)
    backend_caller = BackendCaller(CONFIG.backend)
    try:
        response = backend_caller.post(f"/research/select_listing_by_image",
                                                     json=request.model_dump())
    except Exception as e:
        return {"response": "Failure"}

    return {"response": SelectListingsByImageResponse(**response.json())}