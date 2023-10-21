import time
import sys
import logging
from typing import List
from functools import lru_cache

from fastapi import APIRouter
from selenium.common import NoSuchElementException, ElementNotInteractableException

from digiprod_gen.backend_api.api.common import  CONFIG
from digiprod_gen.backend_api.browser.crawling import mba as mba_crawling
from digiprod_gen.backend_api.browser.parser import mba as mba_parser
from digiprod_gen.backend_api.browser.selenium_fns import wait_until_element_exists, SeleniumBrowser
from digiprod_gen.backend_api.models.mba import CrawlingMBARequest, MBAProduct
from digiprod_gen.backend_api.utils import delete_files_in_path, is_debug


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("BackendAPI")

router = APIRouter()

@lru_cache()
def init_selenium_browser(session_id, proxy=None) -> SeleniumBrowser:
    # New browser is started per session and per proxy
    logger.info(f"Init selenium browser with session_id {session_id}")
    data_dir_path = CONFIG.browser.selenium_data_dir_path
    delete_files_in_path(data_dir_path)
    browser = SeleniumBrowser()
    browser.setup(headless=not is_debug(),
                  data_dir_path=data_dir_path,
                  proxy=proxy
                  )
    return browser

@router.post("/crawling/mba_overview")
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
        wait_until_element_exists(browser.driver, f"//*[@id='nav-global-location-slot'][contains(., '{request.postcode}')]", timeout=4)
        # wait until product images are loaded
        wait_until_element_exists(browser.driver, f"//div[@class='s-image-padding']", timeout=2)
        print("Waited for postcode change %.4f seconds" % (time.time() - ts))
    logger.info("Start parsing information to pydantic objects")
    mba_products: List[MBAProduct] = mba_parser.extract_mba_products(browser.driver, request.marketplace)
    return mba_products


@router.post("/crawling/mba_product")
async def crawl_mba_product(mba_product: MBAProduct, session_id: str, proxy: str | None = None) -> MBAProduct:
    browser = init_selenium_browser(session_id, proxy)
    browser.driver.get(mba_product.product_url)
    mba_product = mba_parser.extend_mba_product(mba_product, driver=browser.driver)
    return mba_product


def init_selenium_browser_working() -> SeleniumBrowser:
    # TODO: Browser would be started with every api call. Better would be to start it per session user
    browser = SeleniumBrowser()
    browser.setup()
    return browser
