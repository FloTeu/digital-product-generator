from typing import Optional, List
from pydantic.v1 import BaseModel, Field
from digiprod_gen.backend.models.mba import MBAMarketplaceDomain, MBAProductCategory
from digiprod_gen.backend.transform.transform_fns import request2mba_overview_url
#from digiprod_gen.backend.models.mba import MBAProduct


class CrawlingMBARequest(BaseModel):
    search_term: str
    marketplace: MBAMarketplaceDomain
    product_category: MBAProductCategory
    mba_overview_url: Optional[str]
    headers: Optional[dict]
    proxy: Optional[str]
    postcode: Optional[str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("mba_overview_url", None) is None:
            self.mba_overview_url = request2mba_overview_url(self)

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

class MBAProductsRequest(BaseModel):
    mba_products: List[MBAProduct] = Field(description="A list of mba_products")


class CrawlMBAProductsDetailRequest(BaseModel):
    mba_products: List[MBAProduct] = Field(description="Single mba_product, which should be crawled for detail information")
    marketplace: MBAMarketplaceDomain


