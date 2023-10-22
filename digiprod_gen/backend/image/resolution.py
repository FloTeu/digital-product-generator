from PIL import Image
from digiprod_gen.backend.image.conversion import pil2bytes_io
from digiprod_gen.backend.image.common import replicate_generate


def real_esrgan_resolution(img_pil: Image) -> Image:
    model = "nightmareai/real-esrgan:42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b"
    return replicate_generate(model, {"image": pil2bytes_io(img_pil)})