from typing import Any
from enum import Enum
from pydantic.v1 import BaseModel

class MemoryId(str, Enum):
    """Defines object in memory and helps the ai agent to reference memory id correct"""
    MBA_PRODUCTS="mba_products"
    SELECTED_MBA_PRODUCTS="mba_products_selected"
    IMAGE_PROMPT="image_prompt"
    IMAGE_RAW="image_raw"
    KEYWORDS="keywords"
    PROMPT_SUGGESTIONS="prompt_suggestions"
    TITLE_SUGGESTIONS="title_suggestions"
    BRAND_SUGGESTIONS="brand_suggestions"
    BULLET_SUGGESTIONS="bullet_suggestions"

class MemoryAddResponse(BaseModel):
    uuid: MemoryId
    success: bool = True
    data: Any | None = None