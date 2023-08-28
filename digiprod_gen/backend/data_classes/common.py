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
    OPENJOURNEY="Openjourney"
    POKEMON="Pokemon"
    WAIFU_DIFFUSION="Waifu"
    MIDJOURNEY="Midjourney"


class MBAMidjourneyOutputModel(BaseModel):
    image_prompts: List[str] = Field(description="List of text-to-image prompts")





