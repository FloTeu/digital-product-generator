from typing import List, Any
from dataclasses import dataclass

import streamlit as st

from digiprod_gen.backend.crawling.proxies import get_random_private_proxy
from digiprod_gen.backend.crawling.mba.utils import get_random_headers
from digiprod_gen.backend.crawling.selenium_fns import SeleniumBrowser
from digiprod_gen.backend.data_classes import CrawlingMBARequest, MBAProductCategory
from digiprod_gen.backend.utils import request2mba_overview_url, is_debug, get_config, delete_files_in_path
from digiprod_gen.backend.crawling.selenium_fns import init_selenium_driver


@dataclass
class SessionState:
    crawling_request: CrawlingMBARequest
    browser: SeleniumBrowser

def create_session_state():
    """Creates a session state if its not already exists"""
    if read_session("session_state") == None:
        config = get_config()
        browser = SeleniumBrowser()
        browser.setup(headless=not is_debug(), data_dir_path=config.selenium_data_dir_path)
        marketplace = st.session_state["marketplace"]
        search_term = st.session_state["search_term"]
        proxy = get_random_private_proxy(st.secrets.proxy_perfect_privacy.user_name,
                                        st.secrets.proxy_perfect_privacy.password, marketplace=marketplace)
        request = CrawlingMBARequest(marketplace=marketplace, product_category=MBAProductCategory.SHIRT,
                                    search_term=search_term, headers=get_random_headers(marketplace), proxy=proxy, mba_overview_url=None)
        request.mba_overview_url = request2mba_overview_url(request)
        session_state = SessionState(crawling_request=request, browser=browser)
        write_session("session_state", session_state)

def write_session(keys: str | List[str], value: Any):
    keys = keys if type(keys) == list else [keys]
    current_session_state = st.session_state
    for i, key in enumerate(keys):
        if key not in current_session_state:
            current_session_state[key] = {}
        # last key
        if i == (len(keys) - 1):
            current_session_state[key] = value
        # Take the current key as next session state
        current_session_state = current_session_state[key]


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
    config = get_config()
    marketplace = st.session_state["marketplace"]
    search_term = st.session_state["search_term"]
    proxy = get_random_private_proxy(st.secrets.proxy_perfect_privacy.user_name,
                                     st.secrets.proxy_perfect_privacy.password, marketplace=marketplace)
    request = CrawlingMBARequest(marketplace=marketplace, product_category=MBAProductCategory.SHIRT,
                                 search_term=search_term, headers=get_random_headers(marketplace), proxy=proxy, mba_overview_url=None)
    request.mba_overview_url = request2mba_overview_url(request)
    write_session("request", request)
    #reset_selenium_driver(None)#config.selenium_data_dir_path)


def reset_selenium_driver(data_dir_path=None):
    """ If possible quits the existing selenium driver and starts a new one"""
    selenium_driver = read_session("selenium_driver")
    try:
        delete_files_in_path(data_dir_path)
        selenium_driver.quit()
    except:
        pass
    selenium_driver = init_selenium_driver(headless=not is_debug(), data_dir_path=data_dir_path)
    write_session("selenium_driver", selenium_driver)
