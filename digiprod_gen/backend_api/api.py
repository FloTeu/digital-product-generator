from typing import List, Annotated
from fastapi import FastAPI, Depends

from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from digiprod_gen.backend_api.models.mba import MBAProduct, CrawlingMBARequest
from digiprod_gen.backend_api.browser.crawling import mba as mba_crawling
from digiprod_gen.backend_api.browser.parser import mba as mba_parser
from digiprod_gen.backend_api.browser.selenium_fns import SeleniumBrowser, wait_until_element_exists
from digiprod_gen.backend_api.utils.utils import delete_files_in_path, is_debug

app = FastAPI()

def init_selenium_browser() -> SeleniumBrowser:
    # TODO: Browser would be started with every api call. Better would be to start it per session user
    data_dir_path = "/tmp/selenium_data" #session_state.config.browser.selenium_data_dir_path
    delete_files_in_path(data_dir_path)
    browser = SeleniumBrowser()
    browser.setup(headless=not is_debug(),
                  data_dir_path=data_dir_path,
                  # proxy=session_state.get_marketplace_config().get_proxy_with_secrets(
                  #     st.secrets.proxy_perfect_privacy.user_name,
                  #     st.secrets.proxy_perfect_privacy.password)
                  )
    return browser


@app.post("/browser/crawling/mba_overview")
async def crawl_mba_overview(request: CrawlingMBARequest, browser: Annotated[SeleniumBrowser, Depends(init_selenium_browser)]) -> List[MBAProduct]:
    """ Searches mba overview page and change postcode in order to see correct products"""
    mba_crawling.search_overview_page(request, browser.driver)
    # If selenium is running with headless mode the first request sometimes fails
    if "something went wrong" in browser.driver.title.lower():
        print("something went wrong during overview crawling. Try again..")
        mba_crawling.search_overview_page(request, browser.driver)
    try:
        mba_crawling.click_ignore_cookies(browser.driver)
    except:
        pass
    if request.postcode:
        print("Try to change postcode")
        try:
            mba_crawling.change_postcode(mba_crawling.driver, request.postcode)
        except (NoSuchElementException, ElementNotInteractableException):
            print("Could not change postcode")
            pass
        wait_until_element_exists(browser.driver, "//*[contains(@class, 'sg-col-inne')]")

    return mba_parser.extract_mba_products(browser.driver, request.marketplace)


@app.post("/browser/crawling/mba_product")
async def crawl_mba_overview(mba_product: MBAProduct, browser: Annotated[SeleniumBrowser, Depends(init_selenium_browser)]) -> MBAProduct:
    browser.driver.get(mba_product.product_url)
    mba_product = mba_parser.extend_mba_product(mba_product, driver=browser.driver)
    return mba_product