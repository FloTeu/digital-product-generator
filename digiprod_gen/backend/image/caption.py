import replicate
import requests

from typing import List
from PIL import Image
from digiprod_gen.backend.image.conversion import pil2bytes_io, bytes2pil
from digiprod_gen.backend.models.mba import MBAProduct
from digiprod_gen.backend.models.session import CrawlingData
from digiprod_gen.backend.models.common import ImageCaptioningModel
from digiprod_gen.backend.utils import booleanize

def image2prompt(img_pil: Image) -> str:
    model = "methexis-inc/img2prompt:50adaf2d3ad20a6f911a8a9e3ccf777b263b8596fbd2c8fc26e8888f8a0edbb5"
    prompt = replicate.run(
        model,
        input={"image": pil2bytes_io(img_pil)}
    )
    return prompt

def has_text_inprint(img_pil: Image) -> bool:
    model = "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608"
    answer = replicate.run(
        model,
        input={"image": pil2bytes_io(img_pil),
               "question": "Does this t-shirt design include a text imprint with several words?"}
    )
    return booleanize(answer)

def image2text_caption(img_pil: Image) -> str:
    model = "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608"
    text_caption = replicate.run(
        model,
        input={"image": pil2bytes_io(img_pil),
               "question": "Write only the text imprint used on this picture"}
    )
    return text_caption

def image2visual_caption(img_pil: Image) -> str:
    model = "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608"
    visual_caption = replicate.run(
        model,
        input={"image": pil2bytes_io(img_pil),
               "question": "Comprehensively describe the visual elements of this image, in order to recreate it"}
    )
    return visual_caption

def extend_mba_products_with_caption(crawling_data: CrawlingData, image_caption_model: ImageCaptioningModel = ImageCaptioningModel.BLIP2):
    mba_products: List[MBAProduct] = crawling_data.get_selected_mba_products()
    for mba_product in mba_products:
        if crawling_data.get_mba_product_image(mba_product.asin) == None:
            crawling_data.mba_product_images[mba_product.asin] = bytes2pil(requests.get(mba_product.image_url, stream=True).content)
        if mba_product.image_text_caption == None:
            img_pil = crawling_data.get_image_design_crop(mba_product.asin)
            if has_text_inprint(img_pil):
                mba_product.image_text_caption = image2text_caption(img_pil)
        if mba_product.image_prompt == None:
            if image_caption_model == ImageCaptioningModel.BLIP2:
                mba_product.image_prompt = image2visual_caption(crawling_data.get_image_design_crop(mba_product.asin))
            elif image_caption_model == ImageCaptioningModel.IMG2PROMPT:
                mba_product.image_prompt = image2prompt(crawling_data.get_image_design_crop(mba_product.asin))
            else:
                raise NotImplementedError
