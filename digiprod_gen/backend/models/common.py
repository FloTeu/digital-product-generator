from typing import List
from pydantic import BaseModel, Field
from enum import Enum


class EnumBase(Enum):
    @classmethod
    def to_list(cls):
        return list(map(lambda c: c.value, cls))


class ImageCaptioningModel(str, Enum):
    BLIP2="Blip 2"
    IMG2PROMPT="Image to Prompt"
    GPT4="gpt-4-vision-preview"

class UpscalerModel(str, Enum):
    PIL="Simple Resize"
    SOME_UPSCALER="AI Upscaler"

class BackgroundRemovalModel(str, Enum):
    OPEN_CV="Simple Background Removal"
    REM_BG="1. AI Background Removal"
    EASY_REM_BG="2. AI Background Removal"

class ImageGenerationModel(str, Enum):
    DALLE_3="DALL-E 3"
    DEEPFLOYD_IF="Deepfloyd IF"
    STABLE_DIFFUSION="Stable Diffusion"
    STABLE_DIFFUSION_BARBIE="Stable Diffusion Barbie"
    STABLE_DIFFUSION_SHIRT="Stable Diffusion Shirt Designs"
    OPENJOURNEY="Openjourney"
    POKEMON="Pokemon"
    WAIFU_DIFFUSION="Waifu"
    MIDJOURNEY="Midjourney"

class ImageGenerationSDXLLoraUrl(str, Enum):
    """Lora fine tuned sdxl model via https://replicate.com/zylim0702/sdxl-lora-customize-training"""
    BARBIE="https://replicate.delivery/pbxt/aEt6InPOlTpZJZ9Y1664pLuWBf5ZdIKdjDK4FmHVB2EA47tIA/trained_model.tar"
    SHIRT="https://replicate.delivery/pbxt/LKrczWaqJqJXCRjRUT4fdKWMpeo5JR2aRoVOg03eppYU6VKjA/trained_model.tar"


# class MBAMidjourneyOutputModel(BaseModel):
#     image_prompts: List[str] = Field(description="List of text-to-image prompts")
#
#
# class MBAProductBrandOutputModel(BaseModel):
#     brands: List[str] = Field(description="List of product brands")
#
# class MBAProductTitleOutputModel(BaseModel):
#     titles: List[str] = Field(description="List of product titles")
#
# class MBAProductBulletsOutputModel(BaseModel):
#     bullets: List[str] = Field(description="List of product bullet point")




