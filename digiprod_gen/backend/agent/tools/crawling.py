import random
from typing import Dict, List

import streamlit as st

from digiprod_gen.backend.agent.constants import NICHES
from digiprod_gen.backend.agent.tools.common import tool

from digiprod_gen.backend.agent.models.api import CrawlingMBARequest
from digiprod_gen.backend.api.common import CONFIG
from digiprod_gen.backend.browser.crawling.utils.utils_mba import get_random_headers
from digiprod_gen.backend.models.mba import MBAMarketplaceDomain, MBAProductCategory, MBAProduct
from digiprod_gen.backend.etl.transform_fns import request2mba_overview_url
from digiprod_gen.backend.agent.memory import global_memory_container
from digiprod_gen.backend.agent.models.memory import MemoryId
from digiprod_gen.frontend.backend_caller import BackendCaller

SESSION_ID: str = "AiAgent"


@tool("crawlOverviewMBATool", args_schema=CrawlingMBARequest, required_memory_ids=[],
      adds_memory_ids=[MemoryId.MBA_PRODUCTS, MemoryId.SEARCH_TERM])
def crawl_overview_mba(search_term: str,
                       marketplace: MBAMarketplaceDomain = MBAMarketplaceDomain.COM,
                       product_category: MBAProductCategory = MBAProductCategory.SHIRT
                       ) -> Dict[str, List[MBAProduct]]:
    """use to crawl amazon mba and receive mba products"""
    # Crawls mba overview page and returns a list of MBAProduct

    proxy = CONFIG.mba.get_marketplace_config(marketplace).get_proxy_with_secrets(
        st.secrets.proxy_perfect_privacy.user_name,
        st.secrets.proxy_perfect_privacy.password)
    postcode = CONFIG.mba.get_marketplace_config(marketplace).postcode
    headers = get_random_headers(marketplace)
    crawling_request: CrawlingMBARequest = CrawlingMBARequest(search_term=search_term,
                                                              marketplace=marketplace,
                                                              product_category=product_category,
                                                              mba_overview_url=None,
                                                              headers=headers,
                                                              proxy=proxy,
                                                              postcode=postcode)

    crawling_request.mba_overview_url = request2mba_overview_url(crawling_request)
    backend_caller = BackendCaller(CONFIG.backend)
    try:
        response = backend_caller.post(f"/browser/crawling/mba_overview?session_id={SESSION_ID}",
                                       json=crawling_request.dict())
    except Exception as e:
        raise e
    if response.status_code != 200:
        raise ValueError("Status code != 200")
    global_memory_container[MemoryId.MBA_PRODUCTS] = [MBAProduct(**product_dict)
                                                      for product_dict in response.json()]
    global_memory_container[MemoryId.SEARCH_TERM] = search_term


@tool("randomSearchTerm", required_memory_ids=[], adds_memory_ids=[MemoryId.SEARCH_TERM])
def get_random_search_term(
) -> Dict[str, str]:
    """use to get search term"""

    search_term = random.choices(NICHES)[0].strip()
    global_memory_container[MemoryId.SEARCH_TERM] = search_term
    return search_term

@tool("crawlProductsMBATool", required_memory_ids=[MemoryId.MBA_PRODUCTS_SELECTED],
      adds_memory_ids=[MemoryId.MBA_PRODUCTS_DETAIL])
def crawl_products_detail_mba(
        marketplace: MBAMarketplaceDomain = MBAMarketplaceDomain.COM
) -> Dict[str, List[MBAProduct]]:
    """use to crawl amazon mba product detail pages and receive list of enriched mba products"""
    mba_products = global_memory_container[MemoryId.MBA_PRODUCTS_SELECTED]

    def crawl_product_mba(mba_product: MBAProduct,
                          marketplace: MBAMarketplaceDomain = MBAMarketplaceDomain.COM
                          ) -> MBAProduct:
        """use to crawl amazon mba and receive enriched mba product"""
        proxy = CONFIG.mba.get_marketplace_config(marketplace).get_proxy_with_secrets(
            st.secrets.proxy_perfect_privacy.user_name,
            st.secrets.proxy_perfect_privacy.password)
        backend_caller = BackendCaller(CONFIG.backend)
        response = backend_caller.post(f"/browser/crawling/mba_product?session_id={SESSION_ID}&proxy={proxy}",
                                       json=mba_product.dict())
        if response.status_code != 200:
            raise ValueError(response.json())
        return MBAProduct(**response.json())

    final_mba_products = []
    for mba_product in mba_products:
        final_mba_products.append(crawl_product_mba(mba_product, marketplace))

    global_memory_container[MemoryId.MBA_PRODUCTS_DETAIL] = final_mba_products
    global_memory_container.status.detail_pages_crawled = True

    return [mba_prod.asin for mba_prod in final_mba_products]
