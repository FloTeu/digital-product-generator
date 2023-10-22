import time
import sys
import logging
from typing import List, Annotated
from functools import lru_cache


from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from selenium.common import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By

from digiprod_gen.backend.api.common import  CONFIG
from digiprod_gen.backend.browser.crawling import mba as mba_crawling
from digiprod_gen.backend.browser.parser import mba as mba_parser
from digiprod_gen.backend.browser.selenium_fns import wait_until_element_exists, SeleniumBrowser
from digiprod_gen.backend.browser.upload import selenium_mba as upload_mba_fns
from digiprod_gen.backend.browser.crawling.utils.common import get_random_user_agent
from digiprod_gen.backend.models.mba import MBAProduct
from digiprod_gen.backend.models.response import UploadMBAResponse
from digiprod_gen.backend.utils import delete_files_in_path, is_debug
from digiprod_gen.backend.models.request import UploadMBARequest, CrawlingMBARequest
from PIL import Image

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("BackendAPI")

security = HTTPBasic()
router = APIRouter()

@lru_cache()
def init_selenium_browser(session_id, proxy=None) -> SeleniumBrowser:
    # New browser is started per session and per proxy
    # get random user agent, each time new browser is created
    user_agent = get_random_user_agent()
    logger.info(f"Init selenium browser with session_id {session_id} and user agent {user_agent}")
    data_dir_path = CONFIG.browser.selenium_data_dir_path
    delete_files_in_path(data_dir_path)
    browser = SeleniumBrowser()
    browser.setup(headless=not is_debug(),
                  data_dir_path=data_dir_path,
                  proxy=proxy,
                  user_agent=user_agent
                  )
    return browser

@router.post("/crawling/mba_overview")
async def crawl_mba_overview(request: CrawlingMBARequest, session_id: str) -> List[MBAProduct]:
    """ Searches utils overview page and change postcode in order to see correct products"""
    #, browser: Annotated[SeleniumBrowser, Depends(init_selenium_browser_working)]
    # browser = SeleniumBrowser()
    # browser.setup()
    browser = init_selenium_browser(session_id, request.proxy)
    logger.info("Start search utils overview page")
    mba_crawling.search_overview_page(request, browser.driver)
    # If selenium is running with headless mode the first request sometimes fails
    first_mba_overview_interactions(browser, request)
    mba_product_web_elements = mba_parser.get_mba_product_web_elements(browser.driver)
    while len(mba_product_web_elements) == 0:
        # Assumption: If no products are displayed, something is wrong with the browser setup
        user_agent = get_random_user_agent()
        logger.info(f"Restart browser with user agent {user_agent}")
        browser.reset_driver(proxy=request.proxy, user_agent=user_agent)
        mba_crawling.search_overview_page(request, browser.driver)
        first_mba_overview_interactions(browser, request)
        mba_product_web_elements = mba_parser.get_mba_product_web_elements(browser.driver)

    # Amazon shows max 48 products on one page
    if request.postcode and len(mba_product_web_elements) < 48:
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
        mba_product_web_elements = mba_parser.get_mba_product_web_elements(browser.driver)

    logger.info("Start parsing information to pydantic objects")
    mba_products: List[MBAProduct] = mba_parser.extract_mba_products(mba_product_web_elements, request.marketplace)
    return mba_products


def first_mba_overview_interactions(browser, request):
    if "something went wrong" in browser.driver.title.lower():
        logger.info("something went wrong during overview crawling. Try again..")
        mba_crawling.search_overview_page(request, browser.driver)
    try:
        logger.info("Click ignore cookie banner")
        mba_crawling.click_ignore_cookies(browser.driver)
    except:
        pass


@router.post("/crawling/mba_product")
async def crawl_mba_product(mba_product: MBAProduct, session_id: str, proxy: str | None = None) -> MBAProduct:
    browser = init_selenium_browser(session_id, proxy)
    browser.driver.get(mba_product.product_url)
    mba_product = mba_parser.extend_mba_product(mba_product, driver=browser.driver)
    return mba_product


@router.get("/upload/mba_login")
async def mba_login(credentials: Annotated[HTTPBasicCredentials, Depends(security)], session_id: str, proxy: str | None = None) -> bool:
    browser = init_selenium_browser(session_id, proxy)
    upload_mba_fns.open_dashboard(browser.driver)
    upload_mba_fns.login_mba(browser.driver, credentials.username, credentials.password)
    # make sure page following is loaded
    time.sleep(3)
    if "OTP" in browser.driver.page_source:
        raise HTTPException(status_code=409, detail="OTP required")
    if "captcha" in browser.driver.page_source.lower():
        raise HTTPException(status_code=409, detail="Captcha required")
    if "your password is incorrect" in browser.driver.page_source.lower():
        raise HTTPException(status_code=401, detail="Wrong credentials")
    elif "verification" not in browser.driver.page_source.lower() and "otp" not in browser.driver.page_source.lower():
        upload_mba_fns.open_dashboard(browser.driver)
        if "merch.amazon.com/dashboard" in browser.driver.current_url:
            # always change to english, in order to have the same html text
            upload_mba_fns.change_language_to_en(browser.driver)
            return True
    return False

@router.get("/upload/mba_login_otp")
async def mba_login_otp(otp_code: str, session_id: str, proxy: str | None = None) -> bool:
    browser = init_selenium_browser(session_id, proxy)
    upload_mba_fns.authenticate_mba_with_opt_code(browser.driver, otp_code)
    upload_mba_fns.wait_until_dashboard_is_ready(browser.driver)
    upload_mba_fns.change_language_to_en(browser.driver)
    return True

@router.post("/upload/upload_mba_product")
async def upload_mba_product(
                             upload_request: UploadMBARequest,
                             session_id: str,
                             image_upload_ready: UploadFile = File(...),
                             proxy: str | None = None) -> UploadMBAResponse:
    """
    Uploads utils product to utils account (without publishing it)
    """
    browser = init_selenium_browser(session_id, proxy)
    image_delete_xpath = "//*[contains(@class, 'sci-delete-forever')]"
    image_pil_upload_ready = Image.open(image_upload_ready.file)
    driver = browser.driver
    upload_mba_fns.open_dashboard(driver)
    upload_mba_fns.open_create_new(driver)
    wait_until_element_exists(driver, "//*[contains(@class, 'product-card')]")

    # Image Upload
    upload_mba_fns.remove_uploaded_image(driver, image_delete_xpath)
    upload_mba_fns.upload_image(browser, image_pil_upload_ready)


    upload_mba_fns.select_products_and_marketplaces(driver,
                                     products=upload_request.settings.product_categories,
                                     marketplaces=upload_request.settings.marketplaces)


    if not upload_request.settings.use_defaults:
        upload_mba_fns.select_colors(driver,
                         colors=upload_request.settings.colors,
                         product_categories=upload_request.settings.product_categories,
                         )
        upload_mba_fns.select_fit_types(driver,
                         fit_types=upload_request.settings.fit_types,
                         product_categories=upload_request.settings.product_categories,
                         )
    # Listing Upload
    # TODO: how to handle case with Marketplace different to com (language of bullets is german for example but form takes englisch text input)
    upload_mba_fns.insert_listing_text(driver, title=upload_request.title,
                        brand=upload_request.brand, bullet_1=upload_request.bullet_1,
                        bullet_2=upload_request.bullet_2,
                        description=upload_request.description)

    wait_until_element_exists(driver, image_delete_xpath)
    # wait some more time just to be sure, that utils is ready for publishing
    time.sleep(3)

    # extract warnings
    # get sibling of warning span tag
    warnings = [w.find_element(By.XPATH, 'following-sibling::*').text
                for w in driver.find_elements(By.XPATH, "//*[contains(@class, 'sci-warning')]")]
    errors = [error_tag.text
                for error_tag in driver.find_elements(By.XPATH, "//*[contains(@class, 'invalid-feedback')]")]
    return UploadMBAResponse(warnings=warnings, errors=errors)


@router.get("/upload/publish_mba_product")
async def publish_mba_product(session_id: str, proxy: str | None = None, searchable: bool = True) -> bool:
    """
    Publishes utils product to marketplace.
    If success return True, otherwise False
    """
    browser = init_selenium_browser(session_id, proxy)
    print("Try to publish utils product")
    upload_mba_fns.publish_to_mba(browser.driver, searchable=searchable)
    time.sleep(1)
    browser.driver.find_element(By.CLASS_NAME, "btn-close").click()
    return True

def init_selenium_browser_working() -> SeleniumBrowser:
    # TODO: Browser would be started with every api call. Better would be to start it per session user
    browser = SeleniumBrowser()
    browser.setup()
    return browser
