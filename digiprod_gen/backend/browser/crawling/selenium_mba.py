from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
import time
from digiprod_gen.backend_api.models.mba import CrawlingMBARequest
from digiprod_gen.backend.browser.selenium_fns import wait_until_element_exists

from selenium.webdriver.chrome.webdriver import WebDriver


def search_overview_page(request: CrawlingMBARequest, driver: WebDriver):
    driver.get(request.mba_overview_url)


def click_ignore_cookies(driver: WebDriver):
    # Click reject all cookies link
    driver.find_element("id", "sp-cc-rejectall-link").click()


def change_postcode(driver, postcode):
    driver.find_element(By.ID, "nav-global-location-popover-link").click()
    time.sleep(1.5)
    try:
        # try to change postcode
        driver.find_element(By.ID, "GLUXChangePostalCodeLink").click()
        time.sleep(0.5)
    except:
        pass
    postcode_input = driver.find_element(By.ID, "GLUXZipUpdateInput")
    postcode_input.send_keys(postcode)

    # Submit the form
    driver.find_element(By.ID, "GLUXZipUpdate").click()  # apply new postcode
    time.sleep(1)

    # submit form
    # Find the element with class "a-popover-footer"
    popover_footer = driver.find_element(By.CLASS_NAME, "a-popover-footer")
    # Find all submit buttons within the "a-popover-footer" element
    submit_buttons = popover_footer.find_elements(
        By.XPATH, ".//input[@type='submit']")
    if len(submit_buttons) == 0:
        submit_buttons = popover_footer.find_elements(By.XPATH, ".//button")
    submit_buttons[0].click()


def search_overview_and_change_postcode(request: CrawlingMBARequest, driver, postcode=None):
    """ Searches mba overview page and change postcode in order to see correct products"""
    search_overview_page(request, driver)
    # If selenium is running with headless mode the first request sometimes fails
    if "something went wrong" in driver.title.lower():
        print("something went wrong during overview crawling. Try again..")
        search_overview_page(request, driver)

    try:
        click_ignore_cookies(driver)
    except:
        pass
    if postcode:
        print("Try to change postcode")
        try:
            change_postcode(driver, postcode)
        except (NoSuchElementException, ElementNotInteractableException):
            print("Could not change postcode")
            pass
        wait_until_element_exists(driver, "//*[contains(@class, 'sg-col-inne')]")
        #time.sleep(3)  # wait until page is refreshed with new products
