from seleniumwire import webdriver
import seleniumwire.undetected_chromedriver as uc
#from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from digiprod_gen.backend_api.utils import delete_files_in_path
from digiprod_gen.backend.image.conversion import bytes2pil

class SeleniumBrowser():
    def __init__(self) -> None:
        self.driver = None
        self.is_ready = False
        self.data_dir_path = None
        self.headless = None
        self.proxy = None

    def setup(self, headless=False, data_dir_path=None, proxy=None):
        self.driver = init_selenium_driver(headless=headless, data_dir_path=data_dir_path, proxy=proxy)
        self.headless = headless
        self.data_dir_path = data_dir_path
        self.is_ready = True
        self.proxy = proxy

    def close_driver(self):
        self.driver.close()
        self.is_ready = False

    def quit_driver(self):
        self.driver.quit()
        self.is_ready = False

    def reset_driver(self, proxy: str | None=None):
        """ If possible quits the existing selenium driver and starts a new one
            Optionally a new proxy can be provided
        """
        try:
            delete_files_in_path(self.data_dir_path)
            self.quit_driver()
        except:
            pass
        self.driver = init_selenium_driver(headless=self.headless, data_dir_path=self.data_dir_path, proxy=proxy or self.proxy)
        if proxy:
            self.proxy = proxy
        self.is_ready = True

def init_selenium_driver(headless=True, data_dir_path=None, proxy: str=None) -> WebDriver:
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
    seleniumwire_options = {}
    if proxy:
        #options.add_argument(f'--proxy-server={proxy}')
        seleniumwire_options = {
            'proxy': {
                'http': proxy,
                #'https': proxy,
                'verify_ssl': False,
                'no_proxy': 'localhost,127.0.0.1'
            },
        }
    if data_dir_path:
        options.add_argument(f'--user-data-dir={data_dir_path}')
    if headless:
        options.add_argument('--headless')
    return webdriver.Chrome(options=options, seleniumwire_options=seleniumwire_options)
    #return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


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

def focus_element(driver: WebDriver, target_element: WebElement):
    # Scroll the element into view using JavaScript
    driver.execute_script("arguments[0].scrollIntoView();", target_element)

def scroll_page(driver: WebDriver, pixel: int):
    """
    Scroll the number of pixels up or down.
    negative pixels mean scrolling up/ postive scrolling down
    """
    scroll_script = f"window.scrollBy(0, {pixel});"
    driver.execute_script(scroll_script)

def scroll_to_top_left(driver: WebDriver):
    # Scroll the entire page to the left using JavaScript
    scroll_script = "window.scrollTo(0, 0);"
    driver.execute_script(scroll_script)

def get_full_page_screenshot(driver: WebDriver) -> bytes:
    """Enhance window size to get full page screenshot"""
    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    # driver.save_screenshot(path)  # has scrollbar
    screenshot_as_png = driver.find_element(By.TAG_NAME, 'body').screenshot_as_png
    driver.set_window_size(original_size['width'], original_size['height'])
    return screenshot_as_png

def has_element_with_class(element: WebElement, class_name):
    elements = element.find_elements(By.CLASS_NAME, class_name)
    return len(elements) > 0

def get_element_html(element: WebElement) -> str:
    return element.get_attribute("outerHTML")

def show_web_element_png(element: WebElement):
    image_pil = bytes2pil(element.screenshot_as_png)
    image_pil.show()

def html2file(driver: WebDriver, file_name: str = "browser.html"):
    """Stores current html of browser to html file"""
    html = driver.page_source
    with open(file_name, "w") as fp:
        fp.write(html)