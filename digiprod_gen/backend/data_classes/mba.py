from dataclasses import dataclass
from enum import Enum
import hashlib
from typing import List, Optional, Union
from PIL import Image


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
    headers: Optional[dict]
    proxy: Optional[str]
    mba_overview_url: Optional[str]

    def get_hash_str(self):
        """Unique hash string which takes all relevant request attributes into account"""
        return hashlib.md5(f'{self.marketplace}{self.search_term}{self.product_category}'.encode()).hexdigest()


@dataclass
class MBAProduct():
    asin: str
    title: str
    brand: Optional[str]
    image_url: str
    product_url: str
    price: Optional[float]
    bullets: Optional[List[str]]
    description: Optional[str]
    image_pil: Optional[Image.Image]
    image_prompt: Optional[str]
    image_text_caption: Optional[str]