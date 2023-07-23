import requests

from typing import Tuple
from PIL import Image
from digiprod_gen.backend.image.conversion import pil2bytes_io, bytes2pil
from digiprod_gen.backend.image.common import replicate_generate, OutputFormat

def pil_upscale(img_pil: Image, shape: Tuple[int, int]) -> Image:
    img_rs = img_pil.resize(shape, resample=Image.BOX)
    print(img_rs.size)
    return img_rs


def some_upscalers_upscale(img_pil: Image) -> Image:
    model = "daanelson/some-upscalers:3078c9717f1b83d4fa86890b769f047695daff189028b96dcf517747853a48b0"
    return replicate_generate(model, {"image": pil2bytes_io(img_pil)})