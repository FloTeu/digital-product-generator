from typing import List, Any

import streamlit as st

from digiprod_gen.backend.crawling.proxies import get_random_private_proxy
from digiprod_gen.backend.crawling.mba.utils import get_random_headers
from digiprod_gen.backend.data_classes import CrawlingMBARequest, MBAProductCategory
from digiprod_gen.backend.utils import request2mba_overview_url



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


def update_mba_request():
    marketplace = st.session_state["marketplace"]
    search_term = st.session_state["search_term"]
    proxy = get_random_private_proxy(st.secrets.proxy_perfect_privacy.user_name, st.secrets.proxy_perfect_privacy.password,marketplace=marketplace)
    request = CrawlingMBARequest(marketplace=marketplace, product_category=MBAProductCategory.SHIRT,
                                 search_term=search_term, headers=get_random_headers(marketplace), proxy=proxy, mba_overview_url=None)
    request.mba_overview_url = request2mba_overview_url(request)
    write_session("request", request)

