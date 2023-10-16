import logging
import time
import io

import sys
from typing import List, Annotated
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from functools import lru_cache

from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from digiprod_gen.backend_api.models.mba import MBAProduct, CrawlingMBARequest
from digiprod_gen.backend_api.browser.crawling import mba as mba_crawling
from digiprod_gen.backend_api.browser.parser import mba as mba_parser
from digiprod_gen.backend_api.browser.selenium_fns import SeleniumBrowser, wait_until_element_exists, get_full_page_screenshot
from digiprod_gen.backend_api.utils.utils import delete_files_in_path, is_debug, initialise_config

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("BackendAPI")

app = FastAPI()
CONFIG = initialise_config("config/app-config.yaml")

@lru_cache()
def init_selenium_browser(session_id, proxy=None) -> SeleniumBrowser:
    logger.info(f"Init selenium browser with session_id {session_id}")
    # TODO: Browser would be started with every api call. Better would be to start it per session user
    data_dir_path = CONFIG.browser.selenium_data_dir_path
    delete_files_in_path(data_dir_path)
    browser = SeleniumBrowser()
    # session_state.get_marketplace_config().get_proxy_with_secrets(
    #     st.secrets.proxy_perfect_privacy.user_name,
    #     st.secrets.proxy_perfect_privacy.password)
    browser.setup(headless=not is_debug(),
                  data_dir_path=data_dir_path,
                  proxy=proxy
                  )
    return browser

def init_selenium_browser_working() -> SeleniumBrowser:
    # TODO: Browser would be started with every api call. Better would be to start it per session user
    browser = SeleniumBrowser()
    browser.setup()
    return browser

@app.post("/browser/crawling/mba_overview")
async def crawl_mba_overview(request: CrawlingMBARequest, session_id: str) -> List[MBAProduct]:
    """ Searches mba overview page and change postcode in order to see correct products"""
    #, browser: Annotated[SeleniumBrowser, Depends(init_selenium_browser_working)]
    # browser = SeleniumBrowser()
    # browser.setup()
    browser = init_selenium_browser(session_id, request.proxy)
    logger.info("Start search mba overview page")
    mba_crawling.search_overview_page(request, browser.driver)
    # If selenium is running with headless mode the first request sometimes fails
    if "something went wrong" in browser.driver.title.lower():
        logger.info("something went wrong during overview crawling. Try again..")
        mba_crawling.search_overview_page(request, browser.driver)
    try:
        logger.info("Click ignore cookie banner")
        mba_crawling.click_ignore_cookies(browser.driver)
    except:
        pass
    if request.postcode:
        logger.info("Try to change postcode")
        try:
            mba_crawling.change_postcode(browser.driver, request.postcode)
        except (NoSuchElementException, ElementNotInteractableException):
            logger.info("Could not change postcode")
            pass
        ts = time.time()
        # wait until postcode change is accepted
        wait_until_element_exists(browser.driver, f"//*[@id='nav-global-location-slot'][contains(., '{request.postcode}')]")
        # wait until product images are loaded
        wait_until_element_exists(browser.driver, f"//div[@class='s-image-padding']")
        print("Waited %.4f seconds" % (time.time() - ts))
    logger.info("Start parsing information to pydantic objects")
    mba_products: List[MBAProduct] = mba_parser.extract_mba_products(browser.driver, request.marketplace)
    return mba_products

@app.post("/browser/crawling/mba_product")
async def crawl_mba_product(mba_product: MBAProduct, session_id: str) -> MBAProduct:
    browser = init_selenium_browser(session_id)
    browser.driver.get(mba_product.product_url)
    mba_product = mba_parser.extend_mba_product(mba_product, driver=browser.driver)
    return mba_product


@app.get("/status/browser_screenshot")
async def get_browser_screenshot(session_id: str, proxy: str | None = None) -> StreamingResponse:
    browser = init_selenium_browser(session_id, proxy)
    screenshot_bytes = get_full_page_screenshot(browser.driver)
    return StreamingResponse(io.BytesIO(screenshot_bytes), media_type="image/png")
