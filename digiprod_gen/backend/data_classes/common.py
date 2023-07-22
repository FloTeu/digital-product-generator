import os
from typing import Dict, List
from pydantic import BaseModel, validator, Field
from pathlib import Path
from enum import Enum

class UpscalerModel(str, Enum):
    PIL="pil"
    SOME_UPSCALER="some_upscaler"

class DigiProdGenMBAMarketplaceConfig(BaseModel):
    postcode: str

class DigiProdGenConfig(BaseModel):
    mba_marketplace: Dict[str, DigiProdGenMBAMarketplaceConfig]
    selenium_data_dir_path: Path

    @validator("selenium_data_dir_path", allow_reuse=True)
    def validate_selenium_data_dir_path(cls, data_dir_path):
        # create dir if not exists
        data_dir_path.mkdir(parents=True, exist_ok=True)
        return data_dir_path

class MBAMidjourneyOutputModel(BaseModel):
    image_prompts: List[str] = Field(description="List of text-to-image prompts")





