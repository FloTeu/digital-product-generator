from typing import List

import requests

from digiprod_gen.backend.image.caption import has_text_inprint, image2text_caption, image2visual_caption, image2prompt
from digiprod_gen.backend.image.conversion import bytes2pil, pil2bytes_io
from digiprod_gen.backend.models.common import ImageCaptioningModel
from digiprod_gen.backend.models.mba import MBAProduct
from digiprod_gen.backend.models.session import CrawlingData
from digiprod_gen.frontend.backend_caller import BackendCaller


def extend_mba_products_with_caption(backend_caller: BackendCaller, crawling_data: CrawlingData, image_caption_model: ImageCaptioningModel = ImageCaptioningModel.GPT4):
    mba_products: List[MBAProduct] = crawling_data.get_selected_mba_products()
    for mba_product in mba_products:
        if crawling_data.get_mba_product_image(mba_product.asin) == None:
            crawling_data.mba_product_images[mba_product.asin] = bytes2pil(requests.get(mba_product.image_url, stream=True).content)

        if mba_product.image_text_caption == None or mba_product.image_prompt == None:
            img_pil = crawling_data.get_image_design_crop(mba_product.asin)
            if mba_product.image_text_caption == None:
                if has_text_inprint(img_pil):
                    mba_product.image_text_caption = backend_caller.post(f"/image/caption?extract_text_caption=true", img_pil=img_pil).json()
            if mba_product.image_prompt == None:
                if image_caption_model:
                    mba_product.image_prompt = backend_caller.post(f"/image/caption?caption_model={image_caption_model.value}", img_pil=img_pil).json()
                else:
                    raise NotImplementedError
