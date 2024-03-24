from typing import List, Any

import streamlit as st

from digiprod_gen.backend.browser.crawling.utils.utils_mba import get_random_headers
from digiprod_gen.backend.browser.selenium_fns import SeleniumBrowser
from digiprod_gen.backend.agent.memory import global_memory_container
from digiprod_gen.backend.agent.models.memory import MemoryId
from digiprod_gen.backend.models.mba import MBAMarketplaceDomain, MBAProductCategory
from digiprod_gen.backend.models.request import CrawlingMBARequest
from digiprod_gen.backend.models.session import SessionState, ImageGenData, CrawlingData, MBAUploadData, \
    DigiProdGenStatus, DigitProdGenViews
from digiprod_gen.backend.models.config import DigiProdGenConfig
from digiprod_gen.frontend.backend_caller import BackendCaller
from digiprod_gen.backend.utils import is_debug, delete_files_in_path
from digiprod_gen.backend.etl.transform_fns import request2mba_overview_url


def creat_session_state(config: DigiProdGenConfig) -> SessionState:
    backend_caller = BackendCaller(config.backend)
    crawling_data = CrawlingData()
    image_gen_data = ImageGenData()
    upload_data = MBAUploadData()
    status = DigiProdGenStatus()
    session_id = get_session_id()
    views = DigitProdGenViews()
    return SessionState(crawling_request=None, browser=None, crawling_data=crawling_data, image_gen_data=image_gen_data,
                        upload_data=upload_data, status=status, session_id=session_id, config=config, backend_caller=backend_caller, views=views)


def start_browser(session_state: SessionState):
    """
    Starts a selenium browser
    Make sure, that session.crawling_request is already initialised
    """
    if session_state.browser == None or not session_state.browser.is_ready:
        data_dir_path = session_state.config.browser.selenium_data_dir_path
        delete_files_in_path(data_dir_path)
        browser = SeleniumBrowser()
        browser.setup(headless=not is_debug(),
                      data_dir_path=data_dir_path,
                      proxy=session_state.get_marketplace_config().get_proxy_with_secrets(
                          st.secrets.proxy_perfect_privacy.user_name,
                          st.secrets.proxy_perfect_privacy.password))
        session_state.browser = browser


def create_mba_request(session_state: SessionState):
    marketplace = read_session("marketplace") or MBAMarketplaceDomain.COM
    search_term = read_session("search_term") or ""
    proxy = session_state.get_marketplace_config(marketplace).get_proxy_with_secrets(
        st.secrets.proxy_perfect_privacy.user_name,
        st.secrets.proxy_perfect_privacy.password)
    # proxy = get_random_private_proxy(st.secrets.proxy_perfect_privacy.user_name,
    #                                  st.secrets.proxy_perfect_privacy.password, marketplace=marketplace)
    request = CrawlingMBARequest(marketplace=marketplace, product_category=MBAProductCategory.SHIRT,
                                 search_term=search_term, headers=get_random_headers(marketplace), proxy=proxy,
                                 mba_overview_url=None)
    request.mba_overview_url = request2mba_overview_url(request)
    session_state.crawling_request = request


def get_session_id():
    return st.runtime.scriptrunner.add_script_run_ctx().streamlit_script_run_ctx.session_id


def init_session_state(config: DigiProdGenConfig):
    """Creates a session state if its not already exists"""
    if "session_state" not in st.session_state:
        st.session_state.session_state = creat_session_state(config)


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

def reset_session_data():
    """
    Some session data depends on search term/ niche that should be created
    This data is not up to date, after search term changed.
    """
    session_data_to_reset = ["final_title", "final_brand", "final_bullet1", "final_bullet2"]
    for session_key in session_data_to_reset:
        if session_key in st.session_state:
            del st.session_state[session_key]

def update_mba_request():
    session_state: SessionState = st.session_state["session_state"]
    if session_state.crawling_request == None:
        create_mba_request(session_state)
    else:
        request = session_state.crawling_request
        previous_marketplace = request.marketplace
        request.marketplace = st.session_state["marketplace"]
        if st.session_state.marketplace != previous_marketplace:
            new_proxy = session_state.get_marketplace_config().get_proxy_with_secrets(
                          st.secrets.proxy_perfect_privacy.user_name,
                          st.secrets.proxy_perfect_privacy.password)
            # As the marketplace changed, we need to update our proxy -> restart browser
            if session_state.browser:
                session_state.browser.reset_driver(
                    proxy=new_proxy
                )
            session_state.crawling_request.proxy = new_proxy

        request.search_term = st.session_state["search_term"]
        request.mba_overview_url = request2mba_overview_url(request)

        # refresh status after request has changed
        session_state.status.refresh()
        session_state.crawling_data.selected_designs = []
    reset_session_data()

def ai_agent_update_mba_products(session_state: SessionState):
    assert MemoryId.MBA_PRODUCTS in global_memory_container
    session_state.status.refresh()
    session_state.status.overview_page_crawled = True
    session_state.crawling_data.mba_products = global_memory_container[MemoryId.MBA_PRODUCTS]

def ai_agent_update_selected_mba_products(session_state: SessionState):
    assert MemoryId.MBA_PRODUCTS_SELECTED in global_memory_container
    # change list of objects to lis of human readable indexes
    list_of_hr_indexes = []
    for i, mba_product in enumerate(session_state.crawling_data.mba_products):
        if any(mba_product.asin == selected_prod.asin for selected_prod in global_memory_container[MemoryId.MBA_PRODUCTS_SELECTED]):
            list_of_hr_indexes.append(i+1) # +1 to make it human readable (same number as human gets displayed
    session_state.crawling_data.selected_designs = list_of_hr_indexes

def ai_agent_update_selected_mba_products_details_crawled(session_state: SessionState):
    assert MemoryId.MBA_PRODUCTS_DETAIL in global_memory_container
    session_state.status.detail_pages_crawled = True
    for i, mba_product in enumerate(session_state.crawling_data.mba_products):
        for selected_prod in global_memory_container[MemoryId.MBA_PRODUCTS_DETAIL]:
            if mba_product.asin == selected_prod.asin:
                session_state.crawling_data.mba_products[i] = selected_prod

def ai_agent_update_prompt_suggestions(session_state: SessionState):
    assert MemoryId.PROMPT_SUGGESTIONS in global_memory_container

    session_state.status.prompts_generated = True
    session_state.image_gen_data.image_gen_prompts = global_memory_container[MemoryId.PROMPT_SUGGESTIONS]

def ai_agent_update_image_generation(session_state: SessionState):
    assert MemoryId.IMAGE_RAW in global_memory_container
    assert MemoryId.IMAGE_PROMPT in global_memory_container

    session_state.image_gen_data.image_gen_prompt_selected = global_memory_container[MemoryId.IMAGE_PROMPT]
    session_state.image_gen_data.image_pil_generated = global_memory_container[MemoryId.IMAGE_RAW]


def ai_agent_update_listing(session_state: SessionState):
    assert MemoryId.KEYWORDS in global_memory_container
    assert MemoryId.BRAND_SUGGESTIONS in global_memory_container
    assert MemoryId.TITLE_SUGGESTIONS in global_memory_container
    assert MemoryId.BULLET_SUGGESTIONS in global_memory_container

    session_state.status.listing_generated = True
    session_state.status.keywords_extracted = True


# # Status update
    # session_state.status.refresh()
    # session_state.status.listing_generated = True
    # session_state.status.prompts_generated = True
    # session_state.status.keywords_extracted = True
    # session_state.status.product_imported = True
    #
    # # Upload data update
    # session_state.upload_data.brand = upload_data.product_data.brand
    # session_state.upload_data.title = upload_data.product_data.title
    # session_state.upload_data.bullet_1 = upload_data.product_data.bullets[0]
    # session_state.upload_data.bullet_2 = upload_data.product_data.bullets[1]
    # session_state.upload_data.description = upload_data.product_data.description
    # session_state.upload_data.predicted_brands = upload_data.processing_data.brand_suggestions
    # session_state.upload_data.predicted_titles = upload_data.processing_data.title_suggestions
    # session_state.upload_data.predicted_bullets = upload_data.processing_data.bullet_suggestions
    # session_state.upload_data.settings = upload_data.mba_upload_settings
    #
    # # image data update
    # session_state.image_gen_data.image_gen_prompts = upload_data.processing_data.prompt_suggestions
    # session_state.image_gen_data.image_gen_prompt_selected = upload_data.processing_data.prompt
    # session_state.image_gen_data.image_pil_generated = img_pil
    # session_state.image_gen_data.image_pil_upscaled = None
    # session_state.image_gen_data.image_pil_background_removed = None
    # session_state.image_gen_data.image_pil_upload_ready = None
    # session_state.image_gen_data.image_pil_outpainted = None
    #
    # # Update session listing
    # st.session_state["final_brand"] = upload_data.product_data.brand
    # st.session_state["final_title"] = upload_data.product_data.title
    # st.session_state["final_bullet1"] = upload_data.product_data.bullets[0]
    # st.session_state["final_bullet2"] = upload_data.product_data.bullets[1]
