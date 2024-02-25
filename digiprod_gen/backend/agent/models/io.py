from typing import List
from pydantic.v1 import BaseModel, Field

#
# class MBAProductIDs(BaseModel):
#     output_size: int


class MBAProductUrls(BaseModel):
    mba_product_urls: List[str]

class MBAProductUploadExport(BaseModel):
    title: str
    brand: str
    bullets: List[str] = Field(description="Two bullets suitable for a good targeting")