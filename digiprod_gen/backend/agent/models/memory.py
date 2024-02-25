from typing import Any
from enum import Enum
from pydantic.v1 import BaseModel

class MemoryId(str, Enum):
    """Defines object in memory and helps the ai agent to reference memory id correct"""
    SEARCH_TERM="search_term"
    MBA_PRODUCTS="mba_products"
    MBA_PRODUCTS_SELECTED= "mba_products_selected"
    MBA_PRODUCTS_DETAIL= "mba_products_detail"
    IMAGE_PROMPT="image_prompt"
    IMAGE_RAW="image_raw"
    KEYWORDS="keywords"
    PROMPT_SUGGESTIONS="prompt_suggestions"
    TITLE_SUGGESTIONS="title_suggestions"
    BRAND_SUGGESTIONS="brand_suggestions"
    BULLET_SUGGESTIONS="bullet_suggestions"
    LISTING_SELECTED="listing_selected"
    EXPORT_DIR="export_dir"


class MemoryAddResponse(BaseModel):
    uuid: MemoryId
    success: bool = True
    data: Any | None = None