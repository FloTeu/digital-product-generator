from typing import List, Annotated
from fastapi import FastAPI, Depends
from digiprod_gen.backend_api.models.mba import MBAProduct, CrawlingMBARequest
from digiprod_gen.backend_api.browser.crawling import mba as mba_crawling
from digiprod_gen.backend_api.browser.selenium_fns import SeleniumBrowser, wait_until_element_exists
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

app = FastAPI()

def init_selenium_browser() -> SeleniumBrowser:
    # TODO: Browser would be started with every api call. Better would be to start it per session user
    browser = SeleniumBrowser()
    browser.setup()
    return browser


@app.post("/browser/crawl_mba_overview")
async def crawl_mba_overview(crawling_request: CrawlingMBARequest, browser: Annotated[SeleniumBrowser, Depends(init_selenium_browser)]) -> List[MBAProduct]:
    """ Searches mba overview page and change postcode in order to see correct products"""
    mba_crawling.search_overview_page(crawling_request, browser.driver)
    # If selenium is running with headless mode the first request sometimes fails
    if "something went wrong" in browser.driver.title.lower():
        print("something went wrong during overview crawling. Try again..")
        mba_crawling.search_overview_page(crawling_request, browser.driver)

    try:
        mba_crawling.click_ignore_cookies(browser.driver)
    except:
        pass
    if crawling_request.postcode:
        print("Try to change postcode")
        try:
            mba_crawling.change_postcode(mba_crawling.driver, crawling_request.postcode)
        except (NoSuchElementException, ElementNotInteractableException):
            print("Could not change postcode")
            pass
        wait_until_element_exists(browser.driver, "//*[contains(@class, 'sg-col-inne')]")

    return [MBAProduct(
        asin="str",
        title="dawawd",
        brand="wad",
        image_url="daw",
        product_url="dwawad",
    )]