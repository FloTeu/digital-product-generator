import time
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from digiprod_gen.backend.data_classes import CrawlingMBARequest, DigiProdGenConfig, MBAMarketplaceDomain



def init_selenium_driver(headless=True) -> WebDriver:
    """Instantiate a WebDriver object (in this case, using Chrome)"""
    options = Options() #either firefox or chrome options
    options.add_argument('--disable-gpu')
    # sandbox may cause error on environments like Docker containers
    options.add_argument('--no-sandbox')
    if headless:
        options.add_argument('--headless')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def close_selenium_driver(driver: WebDriver):
    driver.quit()


# TODO: Refactor folowwing mba functions (upload has also some mba specific functions)
def mba_search_overview_page(request: CrawlingMBARequest, driver: WebDriver):
    return driver.get(request.mba_overview_url)

def mba_click_ignore_cookies(driver: WebDriver):
    # Click reject all cookies link
    driver.find_element("id", "sp-cc-rejectall-link").click()

def mba_change_postcode(driver, postcode):
    driver.find_element(By.ID, "nav-global-location-popover-link").click()
    time.sleep(1)
    try:
        # try to change postcode
        driver.find_element(By.ID, "GLUXChangePostalCodeLink").click()
        time.sleep(0.5)
    except:
        pass
    postcode_input = driver.find_element(By.ID, "GLUXZipUpdateInput")
    postcode_input.send_keys(postcode)

    # Submit the form
    driver.find_element(By.ID, "GLUXZipUpdate").click() # apply new postcode
    time.sleep(0.25)
    # Find all submit buttons on the page
    submit_buttons = driver.find_elements(By.XPATH, "//input[@type='submit']")
    submit_buttons[-1].click()
    #driver.find_element(By.NAME, "glowDoneButton").click() # submit form
    #driver.find_element(By.NAME, "GLUXConfirmClose").click() # submit form


def mba_search_overview_and_change_postcode(request: CrawlingMBARequest, driver, postcode):

    mba_search_overview_page(request, driver)
    # wait to act more like a human
    time.sleep(1)
    try:
        mba_click_ignore_cookies(driver)
    except:
        pass
    try:
        mba_change_postcode(driver, postcode)
    except NoSuchElementException:
        print("Could not change postcode")
        pass
    time.sleep(4) # wait until page is refreshed with new products
    #driver.find_element(By.ID, "GLUXConfirmClose").click() # submit form