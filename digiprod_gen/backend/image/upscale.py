import io
from typing import Tuple
from PIL import Image
from digiprod_gen.backend.image.conversion import pil2bytes_io
from digiprod_gen.backend.image.common import replicate_generate
from digiprod_gen.backend.image.stabilityai import get_upscaling_client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

def pil_upscale(img_pil: Image, shape: Tuple[int, int]) -> Image:
    # https://pillow.readthedocs.io/en/latest/handbook/concepts.html#filters-comparison-table
    img_rs = img_pil.resize(shape, resample=Image.LANCZOS)
    return img_rs


def some_upscalers_upscale(img_pil: Image) -> Image:
    model = "daanelson/some-upscalers:3078c9717f1b83d4fa86890b769f047695daff189028b96dcf517747853a48b0"
    return replicate_generate(model, {"image": pil2bytes_io(img_pil)})

def stability_ai_upscale(img_pil: Image, prompt=None, width=None, client=None) -> Image:
    client = client or get_upscaling_client("stable-diffusion-x4-latent-upscaler")
    answers = client.upscale(
        init_image=img_pil,  # Pass our image to the API and call the upscaling process.
        width=width, # Optional parameter to specify the desired output width.
        prompt=prompt, # Optional parameter when using `stable-diffusion-x4-latent-upscaler` to specify a prompt to use for the upscaling process.
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

def resize_image_keep_aspect_ratio(image: Image, new_width) -> Image:
    """
    Resize an image to a new width while maintaining the aspect ratio.

    :param image: Pillow Image object.
    :param new_width: New width for the resized image.
    :return: Resized Image object.
    """
    original_format = image.format

    # Calculate the new height to maintain aspect ratio
    width_percent = (new_width / float(image.size[0]))
    new_height = int((float(image.size[1]) * float(width_percent)))

    # Resize the image
    resized_image = image.resize((new_width, new_height), resample=Image.LANCZOS)

    # Preserve the original format
    resized_image.format = original_format

    return resized_image
