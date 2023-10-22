import hashlib
import json
from typing import Optional

from pydantic import BaseModel, Field

from digiprod_gen.backend.models.mba import MBAUploadSettings, MBAMarketplaceDomain, MBAProductCategory


class UploadMBARequest(BaseModel):
    title: str
    brand: str
    bullet_1: str | None = None
    bullet_2: str | None = None
    description: str | None = None
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
    postcode: Optional[str] = Field(description="If provided, utils marketplace customer postcode is changed")

    def get_hash_str(self):
        """Unique hash string which takes all relevant request attributes into account"""
        return hashlib.md5(f'{self.marketplace}{self.search_term}{self.product_category}'.encode()).hexdigest()
