from enum import Enum
from typing import List, Optional
from digiprod_gen.backend.models.common import EnumBase
from pydantic import BaseModel, Field


class MBAMarketplaceDomain(str, EnumBase):
    COM="com"
    UK="co.uk"
    DE="de"
    FR="fr"
    IT="it"
    ES="es"
    JP="co.jp"

    def get_webscrapingapi_country_code(self):
        """Get corresponding country code of webscrapingapi.com"""
        if self == "com":
            return "us"
        elif self == "co.uk":
            return "uk"
        elif self == "co.jp":
            return "jp"
        elif self in ["de", "fr", "es", "it"]:
            return self.value
        else:
            raise NotImplementedError


class MBAProductCategory(str, EnumBase):
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

class MBAProductFitType(str, EnumBase):
    MEN="Men"
    WOMAN="Women"
    YOUTH="Youth"


class MBAProductColor(str, EnumBase):
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


class MBAProduct(BaseModel):
    marketplace: MBAMarketplaceDomain
    asin: str
    title: str
    brand: Optional[str] = Field(None)
    image_url: str
    product_url: str
    price: Optional[float] = Field(None)
    description: Optional[str] = Field(None)
    bullets: List[str] = Field(default_factory=list)
    image_prompt: Optional[str] = Field(None)
    image_text_caption: Optional[str] = Field(None)

    class Config:
        arbitrary_types_allowed = True

class MBAUploadSettings(BaseModel):
    use_defaults: bool = Field(default=False)
    product_categories: List[MBAProductCategory] = Field(default_factory=list)
    marketplaces: List[MBAMarketplaceDomain] = Field(default_factory=list)
    colors: List[MBAProductColor] = Field(default_factory=list)
    fit_types: List[MBAProductFitType] = Field(default_factory=list)

    class Config:
        use_enum_values = True

