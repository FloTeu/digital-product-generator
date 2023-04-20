from typing import Tuple
from PIL import Image

def pil_upscale(img_pil: Image, shape: Tuple[int, int]) -> Image:
    img_rs = img_pil.resize(shape, resample=Image.BOX)
    print(img_rs.size)
    return img_rs