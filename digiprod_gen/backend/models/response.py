from typing import List

from pydantic import BaseModel


class UploadMBAResponse(BaseModel):
    warnings: List[str]
    errors: List[str]

class ImageCheckResponse(BaseModel):
    is_suitable: bool
    reason: str