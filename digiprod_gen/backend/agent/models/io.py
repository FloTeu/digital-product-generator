from typing import List
from pydantic.v1 import BaseModel


class MBAProductIDs(BaseModel):
    mba_product_ids: List[str]


class MBAProductUrls(BaseModel):
    mba_product_urls: List[str]