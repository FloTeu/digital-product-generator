import os
import yaml
import streamlit as st

from functools import lru_cache

from pydantic_yaml import parse_yaml_file_as
from digiprod_gen.backend.models.config import DigiProdGenConfig
from digiprod_gen.backend.models.mba import MBAMarketplaceDomain

def init_environment():
    os.environ["OPENAI_API_KEY"] = st.secrets["api_token"]["open_ai"]
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["api_token"]["replicate"]


# @st.cache_resource
# def get_config() -> DigiProdGenConfig:
#     module_file_path = os.path.dirname(digiprod_gen.__file__)
#     return parse_file_as(DigiProdGenConfig, f"{module_file_path}/backend/config.json")

@lru_cache
def initialise_config(config_file_path: str) -> DigiProdGenConfig:
    return parse_yaml_file_as(DigiProdGenConfig, config_file_path)

def booleanize(s):
    return s.lower() in ['true', '1', "y", "yes"]
    
def is_debug():
    return booleanize(os.environ.get("DEBUG", "False"))

def delete_files_in_path(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)

def split_list(list_obj, split_size):
    return [list_obj[i:i+split_size] for i in range(0, len(list_obj), split_size)]

def marketplace2currency(marketplace: MBAMarketplaceDomain) -> str:
    if marketplace == MBAMarketplaceDomain.COM:
        return "$"
    if marketplace == MBAMarketplaceDomain.UK:
        return "£"
    if marketplace == MBAMarketplaceDomain.JP:
        return "¥"
    if marketplace in [MBAMarketplaceDomain.DE, MBAMarketplaceDomain.FR, MBAMarketplaceDomain.IT, MBAMarketplaceDomain.ES]:
        return "€"
    else:
        raise NotImplementedError

def get_price_display_str(marketplace: MBAMarketplaceDomain, price: float, currency: str):
    if marketplace in [MBAMarketplaceDomain.COM, MBAMarketplaceDomain.UK, MBAMarketplaceDomain.JP]:
        return f"{currency}{price}"
    if marketplace in [MBAMarketplaceDomain.DE, MBAMarketplaceDomain.FR, MBAMarketplaceDomain.IT, MBAMarketplaceDomain.ES]:
        return f"{price}{currency}"
    else:
        raise NotImplementedError

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