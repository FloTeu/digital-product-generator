import replicate
import requests

from typing import List
from PIL import Image
from digiprod_gen.backend.image.conversion import pil2bytes_io, bytes2pil
from digiprod_gen.backend.data_classes.mba import MBAProduct

def image2prompt(img_pil: Image) -> str:
    model = "methexis-inc/img2prompt:50adaf2d3ad20a6f911a8a9e3ccf777b263b8596fbd2c8fc26e8888f8a0edbb5"
    prompt = replicate.run(
        model,
        input={"image": pil2bytes_io(img_pil)}
    )
    return prompt

def image2text_caption(img_pil: Image) -> str:
    model = "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608"
    text_caption = replicate.run(
        model,
        input={"image": pil2bytes_io(img_pil),
               "question": "What is the text of this image?"}
    )
    return text_caption

def extend_mba_products_with_caption(mba_products: List[MBAProduct]):
    for mba_product in mba_products:
        if mba_product.image_pil == None:
            mba_product.image_pil = bytes2pil(requests.get(mba_product.image_url, stream=True).content)
        if mba_product.image_text_caption == None:
            mba_product.image_text_caption = image2text_caption(mba_product.image_pil)
        if mba_product.image_prompt == None:
            mba_product.image_prompt = image2prompt(mba_product.image_pil)
