from typing import Optional

import streamlit as st
from langchain_core.tools import tool

from digiprod_gen.backend.agent.models.api import CrawlingMBARequest
from digiprod_gen.backend.api.common import CONFIG
from digiprod_gen.backend.browser.crawling.utils.utils_mba import get_random_headers
from digiprod_gen.backend.models.mba import MBAMarketplaceDomain, MBAProductCategory
from digiprod_gen.backend.transform.transform_fns import request2mba_overview_url
from digiprod_gen.frontend.backend_caller import BackendCaller


@tool("getMbaRequestTool")
def get_crawling_request(search_term) -> CrawlingMBARequest:
    """use to to get mba crawling request"""
    marketplace = MBAMarketplaceDomain.COM
    proxy = CONFIG.mba.get_marketplace_config(marketplace).get_proxy_with_secrets(
        st.secrets.proxy_perfect_privacy.user_name,
        st.secrets.proxy_perfect_privacy.password)
    request = CrawlingMBARequest(marketplace=marketplace, product_category=MBAProductCategory.SHIRT,
                                 search_term=search_term, headers=get_random_headers(marketplace), proxy=proxy,
                                 mba_overview_url=None)
    return {"response": request}


@tool("crawlMBATool", args_schema=CrawlingMBARequest)
def crawl_mba(search_term: str,
                marketplace: MBAMarketplaceDomain,
                product_category: MBAProductCategory,
                mba_overview_url: Optional[str] = None,
                headers: Optional[dict] = None,
                proxy: Optional[str] = None,
                postcode: Optional[str] = None):
    """use to crawl amazon mba and receive mba products"""
    #Crawls mba overview page and returns a list of MBAProduct
    #TODO: handle both cases i.e success and failure
    crawling_request: CrawlingMBARequest = CrawlingMBARequest(search_term=search_term,
                                                            marketplace=marketplace,
                                                            product_category=product_category,
                                                            mba_overview_url=mba_overview_url,
                                                            headers=headers,
                                                            proxy=proxy,
                                                            postcode=postcode)

    crawling_request.mba_overview_url = request2mba_overview_url(crawling_request)
    session_id: str = "AiAgent"
    backend_caller = BackendCaller(CONFIG.backend)
    response = backend_caller.post(f"/browser/crawling/mba_overview?session_id={session_id}",
                                                 json=crawling_request.dict())
    return {"response": response.json()}
