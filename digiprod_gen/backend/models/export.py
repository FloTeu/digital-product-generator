from typing import List

from pydantic import BaseModel

from digiprod_gen.backend.models.mba import MBAUploadSettings
from digiprod_gen.backend.models.session import ProcessingData


class MBAUploadProductData(BaseModel):
    title: str
    brand: str
    bullets: List[str]
    description: str

class MBAUploadData(BaseModel):
    processing_data: ProcessingData
    product_data: MBAUploadProductData
    mba_upload_settings: MBAUploadSettings


