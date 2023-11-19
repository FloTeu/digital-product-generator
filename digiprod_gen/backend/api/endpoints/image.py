import io

from PIL import Image
from fastapi import APIRouter, UploadFile, File
from digiprod_gen.backend.image.caption import image2visual_caption, image2prompt_gpt4, image2prompt, image2text_caption
from digiprod_gen.backend.models.common import ImageCaptioningModel, ImageGenerationModel
from digiprod_gen.backend.image import generation
from fastapi.responses import StreamingResponse


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


@router.get("/generation")
async def get_text_to_image(prompt: str,
                            image_gen_model: ImageGenerationModel) -> StreamingResponse:
    """
    Takes a text2image prompt and creates an image with the provided image_gen_model.
    """

    if image_gen_model == ImageGenerationModel.DEEPFLOYD_IF:
        img_pil = generation.generate_with_deepfloyd_if(prompt)
    elif image_gen_model == ImageGenerationModel.STABLE_DIFFUSION_BARBIE:
        img_pil = generation.generate_with_stable_diffusion_xl_barbie(prompt)
    elif image_gen_model == ImageGenerationModel.STABLE_DIFFUSION_SHIRT:
        img_pil = generation.generate_with_stable_diffusion_xl_shirt(prompt)
    elif image_gen_model == ImageGenerationModel.OPENJOURNEY:
        img_pil = generation.generate_with_openjourney(prompt)
    elif image_gen_model == ImageGenerationModel.STABLE_DIFFUSION:
        img_pil = generation.generate_with_stable_diffusion(prompt)
    elif image_gen_model == ImageGenerationModel.POKEMON:
        img_pil = generation.generate_with_pokemon(prompt)
    elif image_gen_model == ImageGenerationModel.WAIFU_DIFFUSION:
        img_pil = generation.generate_with_waifu(prompt)
    elif image_gen_model == ImageGenerationModel.DALLE_3:
        img_pil = generation.generate_with_dalle3(prompt)
    else:
        raise NotImplementedError

    # Save the Pillow image to a BytesIO object
    img_byte_arr = io.BytesIO()
    img_pil.save(img_byte_arr, format='JPEG')  # Specify the format as needed
    img_byte_arr.seek(0)  # Move to the start of the BytesIO object

    # Create a StreamingResponse, sending the image from the BytesIO object
    return StreamingResponse(img_byte_arr, media_type="image/jpeg")