import io

from PIL import Image
from fastapi import APIRouter, UploadFile, File
from digiprod_gen.backend.image.caption import image2visual_caption, image2prompt_gpt4, image2prompt, image2text_caption
from digiprod_gen.backend.models.common import ImageCaptioningModel


router = APIRouter()

async def get_image(image_file: UploadFile) -> Image:
    contents = await image_file.read()

    # Convert to a BytesIO object
    image_stream = io.BytesIO(contents)

    # Open the image as a Pillow Image
    return Image.open(image_stream)

@router.post("/caption")
async def get_image_caption(caption_model: ImageCaptioningModel = ImageCaptioningModel.GPT4,
                            extract_text_caption: bool=False,
                            image_file: UploadFile = File(...)) -> str:
    """
    Takes an image and creates a highly detailed image caption
    containing the helpful information to create a image prompt.
    """
    img_pil = await get_image(image_file)
    if extract_text_caption:
        return image2text_caption(img_pil)
    else:
        if caption_model == ImageCaptioningModel.BLIP2:
            return image2visual_caption(img_pil)
        elif caption_model == ImageCaptioningModel.IMG2PROMPT:
            return image2prompt(img_pil)
        elif caption_model == ImageCaptioningModel.GPT4:
            return image2prompt_gpt4(img_pil)
