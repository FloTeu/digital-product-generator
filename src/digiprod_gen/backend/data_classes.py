import hashlib
import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict
from pydantic import BaseModel, validator
from pydantic.types import DirectoryPath
from pathlib import Path

class MBAMarketplaceDomain(str, Enum):
    COM="com"
    DE="de"
    UK="co.uk"
    ES="es"
    IT="it"
    FR="fr"
    JP="co.jp"

class MBAProductCategory(str, Enum):
    SHIRT="Shirt"
    PREMIUM_SHIRT="Premium Shirt"
    V_SHIRT="V-neck Shirt"
    TANK_TOP="Tank Top"
    LONG_SLEEVE="Long Sleeve Shirt"
    RAGLAN="Raglan"
    SWEATSHIRT="Sweatshirt"
    HOODIE="Hoodie"
    ZIP_HOODIE="Zip Hoodie"
    POP_SOCKET="Pop Socket"
    IPHONE_CASE="iPhone Case"
    SAMSUNG_GALAXY_CASE="Samsung Galaxy Case"
    TOTE_BAG="Tote Bag"
    THROW_PILLOWS="Throw Pillows"

class MBAProductTextType(str, Enum):
    BRAND="brand"
    TITLE="title"
    BULLET="bullet"


@dataclass
class CrawlingMBARequest():
    search_term: str
    marketplace: MBAMarketplaceDomain
    product_category: MBAProductCategory
    headers: dict
    proxy: Optional[str]
    mba_overview_url: Optional[str]

    def get_hash_str(self):
        """Unique hash string which takes all relevant request attributes into account"""
        return hashlib.md5(f'{self.marketplace}{self.search_term}{self.product_category}'.encode()).hexdigest()


@dataclass
class MBAProduct():
    asin: str
    title: str
    brand: str
    image_url: str
    product_url: str
    price: Optional[float]
    bullets: Optional[List[str]]
    description: Optional[str]

class DigiProdGenMBAMarketplaceConfig(BaseModel):
    postcode: str

class DigiProdGenConfig(BaseModel):
    mba_marketplace: Dict[str, DigiProdGenMBAMarketplaceConfig]
    selenium_data_dir_path: Path

    @validator("selenium_data_dir_path", allow_reuse=True)
    def validate_selenium_data_dir_path(cls, data_dir_path):
        # create dir if not exists
        data_dir_path.mkdir(parents=True, exist_ok=True)
        return data_dir_path

