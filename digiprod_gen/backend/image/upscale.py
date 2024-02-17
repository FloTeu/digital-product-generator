import io
from typing import Tuple
from PIL import Image
from digiprod_gen.backend.image.conversion import pil2bytes_io, pil2b64_str
from digiprod_gen.backend.image.common import replicate_generate, OutputFormat
from digiprod_gen.backend.image.stabilityai import get_upscaling_client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation


def pil_upscale(img_pil: Image, shape: Tuple[int, int]) -> Image:
    # https://pillow.readthedocs.io/en/latest/handbook/concepts.html#filters-comparison-table
    img_rs = img_pil.resize(shape, resample=Image.LANCZOS)
    return img_rs


def some_upscalers_upscale(img_pil: Image) -> Image:
    model = "daanelson/some-upscalers:3078c9717f1b83d4fa86890b769f047695daff189028b96dcf517747853a48b0"
    return replicate_generate(model, {"image": pil2bytes_io(img_pil)})

def gfpgan_upscale(img_pil: Image, scale=16) -> Image:
    model = "alexgenovese/upscaler:ba0132791dea9f3a80b18a9c04e96bdddbc6265e55cb79c61857365f9d172fd8"
    return replicate_generate(model, {"image_url": f"data:image/jpeg;base64,{pil2b64_str(img_pil)}", "scale": scale})

def high_resolution_controlnet_upscale(img_pil: Image, prompt: str) -> Image:
    model = "batouresearch/high-resolution-controlnet-tile:f878e9d044980c8eddb3e449f685945910d86bb55135e45fa065a00a8a519f09"
    return replicate_generate(model, {"image": pil2bytes_io(img_pil), "prompt": prompt, "resolution": 4096, "negative_prompt": "Longbody, lowres, extra digit, fewer digits, cropped, worst quality, low quality, mutant"}, output_format=OutputFormat.GENERATOR)

def ultimate_sd_upscale(img_pil: Image, prompt: str) -> Image:
    model = "fewjative/ultimate-sd-upscale:5daf1012d946160622cd1bd45ed8f12d9675d24659276ccfe24804035f3b3ad7"
    input_params = {"cfg": 8,
        "steps": 20,
        "denoise": 0.2,
        "upscaler": "4x-UltraSharp",
        "mask_blur": 8,
        "mode_type": "Linear",
        "scheduler": "normal",
        "tile_width": 512,
        "upscale_by": 4,
        "tile_height": 512,
        "sampler_name": "euler",
        "tile_padding": 32,
        "seam_fix_mode": "None",
        "seam_fix_width": 64,
        "negative_prompt": "Longbody, lowres, extra digit, fewer digits, cropped, worst quality, low quality, mutant",
        "positive_prompt": prompt,
        "seam_fix_denoise": 1,
        "seam_fix_padding": 16,
        "seam_fix_mask_blur": 8,
        "controlnet_strength": 1,
        "force_uniform_tiles": True,
        "use_controlnet_tile": True
    }
    return replicate_generate(model, {"image": pil2bytes_io(img_pil), **input_params}, output_format=OutputFormat.STRING)

def stability_ai_upscale(img_pil: Image, prompt=None, width=None, client=None) -> Image:
    client = client or get_upscaling_client("stable-diffusion-x4-latent-upscaler")
    answers = client.upscale(
        init_image=img_pil,  # Pass our image to the API and call the upscaling process.
        width=width,  # Optional parameter to specify the desired output width.
        prompt=prompt,
        # Optional parameter when using `stable-diffusion-x4-latent-upscaler` to specify a prompt to use for the upscaling process.
        # seed=1234, # Optional parameter when using `stable-diffusion-x4-latent-upscaler` to specify a seed to use for the upscaling process.
        # steps=20, # Optional parameter when using `stable-diffusion-x4-latent-upscaler` to specify the number of diffusion steps to use for the upscaling process. Defaults to 20 if no value is passed, with a maximum of 50.
        # cfg_scale=7 # Optional parameter when using `stable-diffusion-x4-latent-upscaler` to specify the strength of prompt in use for the upscaling process. Defaults to 7 if no value is passed.
    )
    resp = next(answers)
    artifact = resp.artifacts[0]
    if artifact.type == generation.ARTIFACT_IMAGE:
        return Image.open(io.BytesIO(artifact.binary))
    else:
        raise ValueError("Your request activated the API's safety filters and could not be processed."
                         "Please submit a different image and try again.")


def resize_image_keep_aspect_ratio(img_pil: Image, new_width, resample: str | None = None) -> Image:
    """
    Resize an image to a new width while maintaining the aspect ratio.

    :param img_pil: Pillow Image object.
    :param new_width: New width for the resized image.
    :return: Resized Image object.
    """
    original_format = img_pil.format

    # Calculate the new height to maintain aspect ratio
    width_percent = (new_width / float(img_pil.size[0]))
    new_height = int((float(img_pil.size[1]) * float(width_percent)))

    # Resize the image
    resized_image = img_pil.resize((new_width, new_height), resample=resample)

    # Preserve the original format
    resized_image.format = original_format

    return resized_image
