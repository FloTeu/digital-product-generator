from typing import Dict, List

import streamlit as st
from langchain_core.tools import tool

from digiprod_gen.backend.agent.models.api import CrawlingMBARequest, CrawlMBAProductsDetailRequest
from digiprod_gen.backend.api.common import CONFIG
from digiprod_gen.backend.browser.crawling.utils.utils_mba import get_random_headers
from digiprod_gen.backend.models.mba import MBAMarketplaceDomain, MBAProductCategory, MBAProduct
from digiprod_gen.backend.transform.transform_fns import request2mba_overview_url
from digiprod_gen.frontend.backend_caller import BackendCaller

SESSION_ID: str = "AiAgent"


# @tool("getMbaRequestTool")
# def get_crawling_request(search_term) -> Dict[str, CrawlingMBARequest]:
#     """use to to get mba crawling request"""
#     marketplace = MBAMarketplaceDomain.DE
#     proxy = CONFIG.mba.get_marketplace_config(marketplace).get_proxy_with_secrets(
#         st.secrets.proxy_perfect_privacy.user_name,
#         st.secrets.proxy_perfect_privacy.password)
#     postcode = CONFIG.mba.get_marketplace_config(marketplace).postcode
#     request = CrawlingMBARequest(marketplace=marketplace, product_category=MBAProductCategory.SHIRT,
#                                  search_term=search_term, headers=get_random_headers(marketplace), proxy=proxy,
#                                  postcode=postcode, mba_overview_url=None)
#     return {"response": request}


@tool("crawlOverviewMBATool", args_schema=CrawlingMBARequest)
def crawl_overview_mba(search_term: str,
                       marketplace: MBAMarketplaceDomain = MBAMarketplaceDomain.COM,
                       product_category: MBAProductCategory = MBAProductCategory.SHIRT,
                       backend_caller: BackendCaller = None) -> Dict[str, List[MBAProduct]]:
    """use to crawl amazon mba and receive mba products"""
    #Crawls mba overview page and returns a list of MBAProduct

    proxy = CONFIG.mba.get_marketplace_config(marketplace).get_proxy_with_secrets(
        st.secrets.proxy_perfect_privacy.user_name,
        st.secrets.proxy_perfect_privacy.password)
    postcode = CONFIG.mba.get_marketplace_config(marketplace).postcode
    headers = get_random_headers(marketplace)
    #assert backend_caller
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
        return {"response": "Failure"}
    return {"response": response.json()}


@tool("crawlProductsMBATool", args_schema=CrawlMBAProductsDetailRequest)
def crawl_products_detail_mba(mba_products: List[MBAProduct],
            marketplace: MBAMarketplaceDomain = MBAMarketplaceDomain.COM
            ) -> Dict[str, List[MBAProduct]]:
    """use to crawl amazon mba product detail pages and receive list of enriched mba products"""

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
        return response.json()

    final_mba_products = []
    for mba_product in mba_products:
        try:
            final_mba_products.append(crawl_product_mba(MBAProduct(**mba_product), marketplace))
        except Exception as e:
            return {"response": "Failure"}
    return {"response": final_mba_products}




