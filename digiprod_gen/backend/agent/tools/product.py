import random
from typing import List, Dict

from langchain_core.tools import tool

from digiprod_gen.backend.agent.models.io import MBAProductIDs, MBAProductUrls
from digiprod_gen.backend.models.mba import MBAProduct


@tool("selectMbaProductsTool", args_schema=MBAProductIDs)
def select_mba_products(mba_product_ids: List[str]) -> Dict[str, List[MBAProduct]]:
    """use to select a subsample of mba products for further product generation"""
    # Selects a subsample of suitable mba_products to create new products
    return {"response": random.sample(mba_product_ids, k=min(random.randint(1,9), len(mba_product_ids)))}


@tool("printMbaProductsTool", args_schema=MBAProductUrls)
def print_select_mba_products(mba_product_urls: List[str]):
    """use to print the selected mba products"""
    for mba_product_url in mba_product_urls:
        print(mba_product_url)
    return {"response": "Successfully printed mba products"}
