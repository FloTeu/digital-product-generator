from typing import List

from pydantic import BaseModel

from digiprod_gen.backend.models.mba import MBAUploadSettings
from digiprod_gen.backend.models.session import ProcessingData


class MBAExportUploadProductData(BaseModel):
    title: str
    brand: str
    bullets: List[str]
    description: str

class MBAExportUploadData(BaseModel):
    processing_data: ProcessingData
    product_data: MBAExportUploadProductData
    mba_upload_settings: MBAUploadSettings


