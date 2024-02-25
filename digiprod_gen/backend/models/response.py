from typing import List

from pydantic import BaseModel, Field, field_validator


class UploadMBAResponse(BaseModel):
    warnings: List[str]
    errors: List[str]

class ImageCheckResponse(BaseModel):
    is_suitable: bool
    reason: str

class SelectListingsByImageResponse(BaseModel):
    brand: str = Field(description="Best suitable brand")
    title: str = Field(description="Best suitable title")
    bullets: List[str] = Field(description="Best suitable two bullet points")

    @field_validator('bullets')
    @classmethod
    def list_must_contain_two_values(cls, v: List[str]) -> List[str]:
        if len(v) != 2:
            raise ValueError('List must contain exactly two values')
        return v