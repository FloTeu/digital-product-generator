from typing import List
from pydantic import BaseModel, Field

# Create pydantic in order to define output format
class ImagePromptOutputModel(BaseModel):
    """LLM output format of image prompt generator"""
    few_shot_styles: List[str] = Field(description="Styles existing in the example prompts")
    few_shot_artists: List[str] = Field(description="Artists existing in the example prompts")
    image_prompts: List[str] = Field(description="List of text-to-image prompts")