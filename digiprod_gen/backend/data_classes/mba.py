from dataclasses import dataclass, field
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

class MBAProductFitType(str, Enum):
    MEN="Men"
    WOMAN="Women"
    YOUTH="Youth"


class MBAProductColor(str, Enum):
    ASPHALT_GREY="Asphalt Grey"
    BABY_BLUE="Baby Blue"
    BLACK="Black"
    CRANBERRY_RED="Cranberry Red"
    HEATHER_GREY="Heather Grey"
    DARK_HEATHER_GREY="Dark Heather Grey"
    HEATHER_BLUE="Heather Blue"
    SILVER_GREY="Silver Grey"
    SLATE_GREY="Slate Grey"
    GRASS_GREEN="Grass Green"
    BROWN="Brown"
    KELLY_GREEN="Kelly Green"
    LEMON_YELLOW="Lemon Yellow"
    NAVY_BLUE="Navy Blue"
    OLIVE_GREEN="Olive Green"
    ORANGE="Orange"
    PINK="Pink"
    PURPLE="Purple"
    RED="Red"
    ROYAL="Royal"
    WHITE="White"

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
    description: Optional[str]
    image_pil: Optional[Image.Image]
    image_prompt: Optional[str]
    image_text_caption: Optional[str]
    bullets: List[str] = field(default_factory=list)

    def get_image_design_crop(self):
        if not self.image_pil:
            raise ValueError("Pillow image not yet set")
        width, height = self.image_pil.size
        # Setting the points for cropped image
        left = width / 5
        top = height / 5
        right = 4 * (width / 5)
        bottom = 4 * (height / 5)
        # Cropped image of above dimension
        # (It will not change original image)
        return self.image_pil.crop((left, top, right, bottom))