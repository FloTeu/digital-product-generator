import streamlit as st
from typing import List, Any
from digital_product_generator.data_classes import MBAMarketplaceDomain, CrawlingMBARequest
from digital_product_generator.crawling.utils import get_mba_overview_urls, get_random_headers, is_product_feature_listing

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

def write_session(keys: str | List[str], value: Any):
    keys = keys if type(keys) == list else [keys]
    current_session_dict = st.session_state
    for i, key in enumerate(keys):
        if key not in current_session_dict:
            current_session_dict[key] = {}
        # last key
        if i == (len(keys) - 1):
            current_session_dict[key] = value
        current_session_dict = current_session_dict[key]

def read_session(keys: str | List[str]) -> Any:
    keys = keys if type(keys) == list else [keys]
    current_session_dict = st.session_state
    for i, key in enumerate(keys):
        if key not in current_session_dict:
            return None
        else:
            if i == (len(keys) - 1):
                return current_session_dict[key]
            else:
                current_session_dict = current_session_dict[key]

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