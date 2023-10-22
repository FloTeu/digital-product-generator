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
    brand: Optional[str]
    image_url: str
    product_url: str
    price: Optional[float]
    description: Optional[str]
    bullets: List[str] = Field(default_factory=list)
    image_prompt: Optional[str]
    image_text_caption: Optional[str]
    # TODO: Move to another data class
    # image_pil: Optional[Image.Image]

    class Config:
        arbitrary_types_allowed = True


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


class MBAUploadSettings(BaseModel):
    use_defaults: bool = Field(default=False)
    product_categories: List[MBAProductCategory] = Field(default_factory=list)
    marketplaces: List[MBAMarketplaceDomain] = Field(default_factory=list)
    colors: List[MBAProductColor] = Field(default_factory=list)
    fit_types: List[MBAProductFitType] = Field(default_factory=list)


