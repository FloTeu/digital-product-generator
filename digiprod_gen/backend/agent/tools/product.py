import random
from typing import List, Dict

from langchain_core.tools import tool

from digiprod_gen.backend.agent.models.api import MBAProductsRequest
from digiprod_gen.backend.agent.models.io import MBAProductIDs, MBAProductUrls
from digiprod_gen.backend.api.common import CONFIG
from digiprod_gen.backend.models.mba import MBAProduct
from digiprod_gen.frontend.backend_caller import BackendCaller


@tool("RandomselectMbaProductsTool", args_schema=MBAProductIDs)
def select_random_mba_products(mba_product_ids: List[str]) -> Dict[str, List[MBAProduct]]:
    """use to select a subsample of mba products for further product generation"""
    # Selects a subsample of suitable mba_products to create new products
    return {"response": random.sample(mba_product_ids, k=min(random.randint(1,4), len(mba_product_ids)))}


@tool("printMbaProductsTool", args_schema=MBAProductsRequest)
def print_select_mba_products(mba_products: List[MBAProduct]):
    """use to print the selected mba products"""
    for mba_product in mba_products:
        print(MBAProduct(**mba_product).json())
    return {"response": "Successfully printed mba products"}


@tool("selectMBAProductsTool", args_schema=MBAProductsRequest)
def select_mba_products(mba_products: List[MBAProduct]) -> Dict[str, List[str]]:
    """
    Takes all crawled mba products and creates chooses the best suitable products
    for further processing via AI technology.
    """

    request = MBAProductsRequest(mba_products=mba_products)
    backend_caller = BackendCaller(CONFIG.backend)
    try:
        response = backend_caller.post(f"/research/select_products",
                                                     json=request.dict())
    except Exception as e:
        return {"response": "Failure"}
    return {"response": response.json()}
#
# @tool("selectMBAProductsTool", args_schema=MBAProductsRequest)
# def select_products(mba_products: List[MBAProduct]) -> Dict[str, List[str]]:
#     """
#     Takes all crawled mba products and creates chooses the best suitable products
#     for further processing via AI technology.
#     """
#
#     request = MBAProductsRequest(mba_products=mba_products)
#     backend_caller = BackendCaller(CONFIG.backend)
#     try:
#         response = backend_caller.post(f"/research/select_products",
#                                                      json=request.dict())
#     except Exception as e:
#         return {"response": "Failure"}
#     return {"response": response.json()}
