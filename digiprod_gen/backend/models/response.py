from typing import List

from pydantic import BaseModel


class UploadMBAResponse(BaseModel):
    warnings: List[str]
    errors: List[str]
