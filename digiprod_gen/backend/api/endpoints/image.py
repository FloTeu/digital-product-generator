import io

from PIL import Image
from fastapi import APIRouter, UploadFile, File
from digiprod_gen.backend.image.caption import image2visual_caption, image2prompt_gpt4, image2prompt, image2text_caption
from digiprod_gen.backend.models.common import ImageCaptioningModel, ImageGenerationModel, UpscalerModel, BackgroundRemovalModel
from digiprod_gen.backend.image.upscale import pil_upscale, some_upscalers_upscale, gfpgan_upscale, high_resolution_controlnet_upscale
from digiprod_gen.backend.image.background_removal import simple_remove_background, rembg, easy_rem_bg
from digiprod_gen.backend.image import generation, conversion
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
        else:
            raise NotImplementedError


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
    img_byte_arr = conversion.pil2bytes_io(img_pil, format="JPEG")
    img_byte_arr.seek(0)  # Move to the start of the BytesIO object

    # Create a StreamingResponse, sending the image from the BytesIO object
    return StreamingResponse(img_byte_arr, media_type="image/jpeg")


@router.post("/upscaling")
async def get_image_upscaled(upscaler: UpscalerModel, prompt: str="", image_file: UploadFile = File(...)) -> StreamingResponse:
    """
    Takes an image and scales it up to 4xxx pixel width and height
    """
    img_pil = conversion.pilrgba2pilrgb(await get_image(image_file))
    if upscaler == UpscalerModel.PIL:
        image_pil_upscaled = pil_upscale(img_pil, (4500, 4500))
        # increase resolution after simple upscale
        # image_pil_upscaled = real_esrgan_resolution(image_pil_upscaled)
    elif upscaler == UpscalerModel.GFPGAN:
        image_pil_upscaled = gfpgan_upscale(img_pil, scale=int((4096 / img_pil.size[0]) * 2))
    elif upscaler == UpscalerModel.HIGH_RESOLUTION_CONTROLNET:
        image_pil_upscaled = high_resolution_controlnet_upscale(img_pil, prompt=prompt)
    elif upscaler == UpscalerModel.SOME_UPSCALER:
        # Convert 4 channels to 3 channels
        image_pil_upscaled = some_upscalers_upscale(img_pil)
    else:
        raise NotImplementedError

    # Save the Pillow image to a BytesIO object
    img_byte_arr = conversion.pil2bytes_io(image_pil_upscaled, format="JPEG")
    img_byte_arr.seek(0)  # Move to the start of the BytesIO object

    # Create a StreamingResponse, sending the image from the BytesIO object
    return StreamingResponse(img_byte_arr, media_type="image/jpeg")

@router.post("/background_removal")
async def get_image_background_removed(br_method: BackgroundRemovalModel,
                                       outer_pixel_range: int = 30,
                                       tolerance: int = 100,
                                       image_file: UploadFile = File(...)) -> StreamingResponse:
    """
    Takes an image and removes the background
    """
    img_pil = await get_image(image_file)
    assert img_pil.mode == "RGB"

    if br_method == BackgroundRemovalModel.OPEN_CV:
        image_pil_br = simple_remove_background(img_pil, outer_pixel_range=outer_pixel_range, tolerance=tolerance)
    elif br_method == BackgroundRemovalModel.REM_BG:
        image_pil_br = rembg(img_pil)
    elif br_method == BackgroundRemovalModel.EASY_REM_BG:
        image_pil_br = easy_rem_bg(img_pil)
    else:
        raise NotImplementedError

    # After background is removed the pillow image should have a alpha channel
    assert image_pil_br.mode == "RGBA"
    # Save the Pillow image to a BytesIO object
    img_byte_arr = conversion.pil2bytes_io(image_pil_br, format="PNG")
    img_byte_arr.seek(0)  # Move to the start of the BytesIO object

    # Create a StreamingResponse, sending the image from the BytesIO object
    return StreamingResponse(img_byte_arr, media_type="image/png")
