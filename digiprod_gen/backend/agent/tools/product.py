import random
import requests
import json
from datetime import datetime
from typing import List, Dict
from pydantic.json import pydantic_encoder

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
from digiprod_gen.backend.agent.tools.common import tool
from digiprod_gen.frontend.backend_caller import BackendCaller

@tool("randomselectMbaProductsTool", required_memory_ids=[MemoryId.MBA_PRODUCTS], adds_memory_ids=[MemoryId.SELECTED_MBA_PRODUCTS])

def select_random_mba_products(output_size: int = 4) -> Dict[str, MemoryAddResponse]:
    """use to select a subsample of mba products for further product generation"""
    mba_products = global_memory_container[MemoryId.MBA_PRODUCTS]
    mba_products_selected = random.choices(mba_products,k=output_size)
    global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS] = mba_products_selected

@tool("printMbaProductsTool", required_memory_ids=[MemoryId.MBA_PRODUCTS, MemoryId.SELECTED_MBA_PRODUCTS], adds_memory_ids=[])
def print_select_mba_products():
    """use to print the selected mba products"""
    mba_products = global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS]
    for mba_product in mba_products:
        print(mba_product.json())
    return {"response": "Successfully printed mba products"}

@tool("selectMBAProductsTool", required_memory_ids=[MemoryId.MBA_PRODUCTS], adds_memory_ids=[MemoryId.SELECTED_MBA_PRODUCTS])
def select_mba_products() -> Dict[str, MemoryAddResponse]:
    """
    Takes all crawled mba products and creates chooses the best suitable products
    for further processing via AI technology.
    """
    mba_products = global_memory_container[MemoryId.MBA_PRODUCTS]

    request = MBAProductsRequest(mba_products=mba_products)
    backend_caller = BackendCaller(CONFIG.backend)
    response = backend_caller.post(f"/research/select_products",
                                                 json=request.dict())
    response.raise_for_status()

    selected_asins = response.json()
    selected_mba_products = [mba_product for mba_product in mba_products if mba_product.asin in selected_asins]

    global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS] = selected_mba_products

@tool("enrichMBAProductsWithImageCaptionTool", required_memory_ids=[MemoryId.MBA_PRODUCTS, MemoryId.SELECTED_MBA_PRODUCTS], adds_memory_ids=[MemoryId.SELECTED_MBA_PRODUCTS])
def enrich_mba_products_with_image_caption(
                    caption_model: ImageCaptioningModel = ImageCaptioningModel.GPT4
                    ) -> Dict[str, MemoryAddResponse]:
    """
    Takes s subsample of crawled mba products and adds the image_prompt attribute.
    """
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



@tool("getPromptSuggestionsTool", required_memory_ids=[MemoryId.MBA_PRODUCTS, MemoryId.SELECTED_MBA_PRODUCTS], adds_memory_ids=[MemoryId.PROMPT_SUGGESTIONS])
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
    response.raise_for_status()
    prompt_suggestions = response.json()
    global_memory_container.status.prompts_generated = True
    global_memory_container[MemoryId.PROMPT_SUGGESTIONS] = prompt_suggestions
    return prompt_suggestions

@tool("generateImageTool", required_memory_ids=[MemoryId.MBA_PRODUCTS, MemoryId.SELECTED_MBA_PRODUCTS, MemoryId.PROMPT_SUGGESTIONS], adds_memory_ids=[MemoryId.IMAGE_RAW, MemoryId.IMAGE_PROMPT])
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
    response.raise_for_status()
    image_pil_generated = conversion.bytes2pil(response.content)
    image_pil_generated.save(f"export/{search_term}_{str(datetime.now())}.png")
    global_memory_container[MemoryId.IMAGE_RAW] = image_pil_generated
    global_memory_container[MemoryId.IMAGE_PROMPT] = prompt

@tool("evaluateImageTool", required_memory_ids=[MemoryId.MBA_PRODUCTS, MemoryId.SELECTED_MBA_PRODUCTS, MemoryId.PROMPT_SUGGESTIONS, MemoryId.IMAGE_RAW], adds_memory_ids=[])
def evaluate_image(
                    prompt: str
                    ) -> Dict[str, Dict[str, ImageCheckResponse]]:
    """
    Checks whether image is suitable for a print on demand design.
    """
    img_pil = global_memory_container[MemoryId.IMAGE_RAW]
    backend_caller = BackendCaller(CONFIG.backend)
    response = backend_caller.post(f"/image/check?prompt={prompt}", img_pil=img_pil)
    response.raise_for_status()
    return {"response": response.json()}

@tool("extractKeywords", required_memory_ids=[MemoryId.MBA_PRODUCTS, MemoryId.SELECTED_MBA_PRODUCTS], adds_memory_ids=[MemoryId.KEYWORDS])
def extract_keywords(
                    ) -> Dict[str, MemoryAddResponse]:
    """
    Extract keywords from crawled mba products
    """
    backend_caller = BackendCaller(CONFIG.backend)
    mba_products = global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS]

    keyword_text = ""
    for mba_product in mba_products:
        keyword_text += f"{mba_product.brand} {mba_product.title} {' '.join([bullet for bullet in mba_product.bullets])}\n"
    KeywordExtractionRequest(text=keyword_text)
    response = backend_caller.post(f"/text/extract/keywords", data=KeywordExtractionRequest(text=keyword_text).model_dump_json())
    response.raise_for_status()

    global_memory_container[MemoryId.KEYWORDS] = response.json()
    global_memory_container.status.keywords_extracted = True

@tool("generateListingSuggestions", required_memory_ids=[MemoryId.MBA_PRODUCTS, MemoryId.SELECTED_MBA_PRODUCTS, MemoryId.KEYWORDS], adds_memory_ids=[])
def generate_listing_suggestions(
        product_type: MBAProductTextType
        ) -> Dict[str, MemoryAddResponse]:
    """
    Generates listing suggestions such as title, brand or bullets
    """

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
    response.raise_for_status()

    listing_suggestion = response.json()
    global_memory_container[memory_id] = listing_suggestion
    type_in_memory_list = [product_type_i in global_memory_container for product_type_i in
     [MemoryId.BRAND_SUGGESTIONS, MemoryId.TITLE_SUGGESTIONS, MemoryId.BULLET_SUGGESTIONS]]
    if all(type_in_memory_list):
        print("All listings successfully generated")
        global_memory_container.status.listing_generated = True

    return {"response": MemoryAddResponse(uuid=memory_id, success=True, data=None)}


@tool("selectMBAListingsTool", required_memory_ids=[MemoryId.MBA_PRODUCTS, MemoryId.SELECTED_MBA_PRODUCTS, MemoryId.KEYWORDS, MemoryId.TITLE_SUGGESTIONS, MemoryId.BRAND_SUGGESTIONS, MemoryId.BULLET_SUGGESTIONS], adds_memory_ids=[MemoryId.LISTING_SELECTED])
def select_mba_listings() -> Dict[str, SelectListingsByImageResponse]:
    """
    Takes ai generated mba product image and listing suggestions and decides which
    listing suggestion (i.e. title, brand, bullets) is the best suitable for the image.
    """
    title_suggestions = global_memory_container[MemoryId.TITLE_SUGGESTIONS]
    brand_suggestions = global_memory_container[MemoryId.BRAND_SUGGESTIONS]
    bullet_suggestions = global_memory_container[MemoryId.BULLET_SUGGESTIONS]
    img_pil = global_memory_container[MemoryId.IMAGE_RAW]

    request = SelectListingsByImageRequest(img_b64_str=conversion.pil2b64_str(img_pil),
                                           title_suggestions=title_suggestions,
                                           brand_suggestions=brand_suggestions,
                                           bullet_suggestions=bullet_suggestions)
    backend_caller = BackendCaller(CONFIG.backend)
    response = backend_caller.post(f"/research/select_listing_by_image",
                                                 json=request.model_dump())
    response.raise_for_status()

    return {"response": SelectListingsByImageResponse(**response.json())}