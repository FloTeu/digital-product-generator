import streamlit as st
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from digiprod_gen.backend.data_classes.config import DigiProdGenConfig
from digiprod_gen.backend.data_classes.mba import MBAMarketplaceDomain
from digiprod_gen.backend.image.conversion import bytes2pil
from digiprod_gen.backend.utils import delete_files_in_path


class SeleniumBrowser():
    def __init__(self) -> None:
        self.driver = None
        self.is_ready = False
        self.data_dir_path = None
        self.headless = None

    def setup(self, headless=False, data_dir_path=None):
        self.driver = init_selenium_driver(headless=headless, data_dir_path=data_dir_path)
        self.headless = headless
        self.data_dir_path = data_dir_path
        self.is_ready = True

    def close_driver(self):
        self.driver.close()
        self.is_ready = False

    def quit_driver(self):
        self.driver.quit()
        self.is_ready = False

    def reset_driver(self):
        """ If possible quits the existing selenium driver and starts a new one"""
        try:
            delete_files_in_path(self.data_dir_path)
            self.quit_driver()
        except:
            pass
        self.driver = init_selenium_driver(headless=self.headless, data_dir_path=self.data_dir_path)
        self.is_ready = True

def init_selenium_driver(headless=True, data_dir_path=None) -> WebDriver:
    """Instantiate a WebDriver object (in this case, using Chrome)"""
    options = Options() #either firefox or chrome options
    options.add_argument('--disable-gpu')
    # sandbox may cause error on environments like Docker containers
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")
    #options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--disk-cache-size=10000000')  # Set cache size to 10 MB
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("−−lang=en") # language english
    if data_dir_path:
        options.add_argument(f'--user-data-dir={data_dir_path}')
    if headless:
        options.add_argument('--headless')
    return webdriver.Chrome(options=options)
    #return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def show_web_element_png(element: WebElement):
    image_pil = bytes2pil(element.screenshot_as_png)
    image_pil.show()


def hover_over_element(driver: WebDriver, element_to_hover):
    # Create an instance of ActionChains and pass the driver as a parameter.
    action_chains = ActionChains(driver)

    # Perform the hover action on the element.
    action_chains.move_to_element(element_to_hover).perform()

def wait_until_element_exists(driver: WebDriver, xpath: str, timeout: int=10) -> WebElement | None:
    """
    driver: chromium driver
    timeout: Maximum time to wait for the element to appear (in seconds).
    """

    try:
        # Wait until the element with the specified ID appears on the page.
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element
    except Exception as e:
        # If the element does not appear within the specified timeout, an exception will be raised.
        print(f"Error with xpath {xpath}:", type(e))