import os

from digiprod_gen.backend.crawling.mba.utils import get_mba_overview_urls
from digiprod_gen.backend.data_classes import (CrawlingMBARequest,
                                               MBAMarketplaceDomain)


def is_debug():
    return bool(os.environ.get("DEBUG", False))

def split_list(list_obj, split_size):
    return [list_obj[i:i+split_size] for i in range(0, len(list_obj), split_size)]

def marketplace2currency(marketplace: MBAMarketplaceDomain) -> str:
    if marketplace == MBAMarketplaceDomain.COM:
        return "$"
    if marketplace in [MBAMarketplaceDomain.DE]:
        return "€"
    else:
        raise NotImplementedError

def get_price_display_str(marketplace: MBAMarketplaceDomain, price: float, currency: str):
    if marketplace == MBAMarketplaceDomain.COM:
        return f"{currency}{price}"
    if marketplace in [MBAMarketplaceDomain.DE]:
        return f"{price}{currency}"
    else:
        raise NotImplementedError

def request2mba_overview_url(request: CrawlingMBARequest) -> str:
    start_page = 0
    number_pages = 1
    mba_urls = get_mba_overview_urls(
        marketplace=request.marketplace,
        search_term=request.search_term,
        product_category=request.product_category,
        start_page=start_page,
        number_pages=number_pages
    )
    return mba_urls[0]


# def generate_caption(processor, model, image: Image, tokenizer=None, use_float_16=False, device="cpu"):
#     inputs = processor(images=image, return_tensors="pt").to(device)
#
#     if use_float_16:
#         inputs = inputs.to(torch.float16)
#
#     generated_ids = model.generate(pixel_values=inputs.pixel_values, max_length=50)
#
#     if tokenizer is not None:
#         generated_caption = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
#     else:
#         generated_caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
#
#     return generated_caption