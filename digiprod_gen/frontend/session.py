from typing import List, Any

import streamlit as st

from digiprod_gen.backend.browser.crawling.proxies import get_random_private_proxy
from digiprod_gen.backend.browser.crawling.mba.utils import get_random_headers
from digiprod_gen.backend.browser.selenium_fns import SeleniumBrowser, init_selenium_driver
from digiprod_gen.backend.data_classes.mba import CrawlingMBARequest, MBAMarketplaceDomain, MBAProductCategory
from digiprod_gen.backend.data_classes.session import SessionState, ImageGenData, CrawlingData, MBAUploadData, DigiProdGenStatus
from digiprod_gen.backend.utils import request2mba_overview_url, is_debug, get_config, delete_files_in_path

def creat_session_state() -> SessionState:
    crawling_data=CrawlingData()
    image_gen_data = ImageGenData()
    upload_data = MBAUploadData()
    status = DigiProdGenStatus()
    session_id = get_session_id()
    return SessionState(crawling_request=None, browser=None, crawling_data=crawling_data, image_gen_data=image_gen_data, upload_data=upload_data, status=status, session_id=session_id)

def start_browser(session_state: SessionState):
    if session_state.browser == None or not session_state.browser.is_ready:
        config = get_config()
        delete_files_in_path(config.selenium_data_dir_path)
        browser = SeleniumBrowser()
        browser.setup(headless=not is_debug(),
                        data_dir_path=config.selenium_data_dir_path)
        session_state.browser = browser

def create_mba_request(session_state: SessionState):
    marketplace = read_session("marketplace") or MBAMarketplaceDomain.COM
    search_term = read_session("search_term") or ""
    proxy = get_random_private_proxy(st.secrets.proxy_perfect_privacy.user_name,
                                        st.secrets.proxy_perfect_privacy.password, marketplace=marketplace)
    request = CrawlingMBARequest(marketplace=marketplace, product_category=MBAProductCategory.SHIRT,
                                    search_term=search_term, headers=get_random_headers(marketplace), proxy=proxy, mba_overview_url=None)
    request.mba_overview_url = request2mba_overview_url(request)
    session_state.crawling_request = request



def get_session_id():
    return st.runtime.scriptrunner.add_script_run_ctx().streamlit_script_run_ctx.session_id

def set_session_state_if_not_exists():
    """Creates a session state if its not already exists"""
    if read_session("session_state") == None:
        write_session("session_state", creat_session_state())

def init_session_state():
    """Creates a session state if its not already exists"""
    if "session_state" not in st.session_state:
        st.session_state.session_state = creat_session_state()


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
    session_state: SessionState = st.session_state["session_state"]
    if session_state.crawling_request == None:
        create_mba_request(session_state)
    else:
        request = session_state.crawling_request
        request.marketplace = st.session_state["marketplace"]
        request.search_term = st.session_state["search_term"]
        request.mba_overview_url = request2mba_overview_url(request)

        # TODO: Maybe reset also other status as well
        session_state.status.overview_page_crawled = False


