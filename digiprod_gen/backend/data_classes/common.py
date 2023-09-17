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

class UpscalerModel(str, Enum):
    PIL="Simple Resize"
    SOME_UPSCALER="AI Upscaler"

class BackgroundRemovalModel(str, Enum):
    OPEN_CV="Simple Background Removal"
    REM_BG="AI Background Removal"

class ImageGenerationModel(str, Enum):
    DEEPFLOYD_IF="Deepfloyd IF"
    STABLE_DIFFUSION="Stable Diffusion"
    STABLE_DIFFUSION_BARBIE="Stable Diffusion Barbie"
    OPENJOURNEY="Openjourney"
    POKEMON="Pokemon"
    WAIFU_DIFFUSION="Waifu"
    MIDJOURNEY="Midjourney"

class ImageGenerationSDXLLoraUrl(str, Enum):
    """Lora fine tuned sdxl model via https://replicate.com/zylim0702/sdxl-lora-customize-training"""
    BARBIE="https://replicate.delivery/pbxt/aEt6InPOlTpZJZ9Y1664pLuWBf5ZdIKdjDK4FmHVB2EA47tIA/trained_model.tar"


class MBAMidjourneyOutputModel(BaseModel):
    image_prompts: List[str] = Field(description="List of text-to-image prompts")





