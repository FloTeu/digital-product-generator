import hashlib
import json
from typing import Optional, List, Dict

from pydantic import BaseModel, Field

from digiprod_gen.backend.models.mba import MBAUploadSettings, MBAMarketplaceDomain, MBAProductCategory, MBAProduct, MBAProductTextType

class UploadMBARequest(BaseModel):
    title: str
    brand: str
    bullet_1: str | None = Field(None)
    bullet_2: str | None = Field(None)
    description: str | None = Field(None)
    settings: MBAUploadSettings = Field(default_factory=MBAUploadSettings)


    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class CrawlingMBARequest(BaseModel):
    search_term: str
    marketplace: MBAMarketplaceDomain
    product_category: MBAProductCategory
    headers: Optional[dict]
    proxy: Optional[str]
    mba_overview_url: Optional[str]
    postcode: Optional[str] = Field(None, description="If provided, utils marketplace customer postcode is changed")

    def get_hash_str(self):
        """Unique hash string which takes all relevant request attributes into account"""
        return hashlib.md5(f'{self.marketplace}{self.search_term}{self.product_category}'.encode()).hexdigest()

class KeywordExtractionRequest(BaseModel):
    text: str
    remove_banned_words: bool = True

class ListingGenRequest(BaseModel):
    examples: List[str]
    keywords: str
    type: MBAProductTextType
    remove_banned_words: bool = True


class SelectProductRequest(BaseModel):
    id2asin: Dict[int, str]
    img_b64_str: str


class MBAProductsRequest(BaseModel):
    mba_products: List[MBAProduct]


class SelectListingsByImageRequest(BaseModel):
    img_b64_str: str
    brand_suggestions: List[str]
    title_suggestions: List[str]
    bullet_suggestions: List[str]
