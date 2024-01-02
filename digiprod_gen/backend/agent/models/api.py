from typing import Optional
from pydantic.v1 import BaseModel
from digiprod_gen.backend.models.mba import MBAMarketplaceDomain, MBAProductCategory
from digiprod_gen.backend.transform.transform_fns import request2mba_overview_url


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





