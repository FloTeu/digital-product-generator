import logging

from seleniumwire import webdriver
#from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from digiprod_gen.backend.utils import delete_files_in_path
from digiprod_gen.backend.image.conversion import bytes2pil

class SeleniumBrowser():
    def __init__(self) -> None:
        self.driver = None
        self.is_ready = False
        self.data_dir_path = None
        self.headless = None
        self.proxy = None
        self.user_agent = None
        self.headers = None
        self.allow_javascript = None
        self.disable_images = None

    def setup(self, headless=False, data_dir_path=None, proxy=None, user_agent=None, headers=None, allow_javascript=None, disable_images=None):
        # get default bool if None provided
        allow_javascript = False if allow_javascript is None else allow_javascript
        disable_images = True if disable_images is None else disable_images
        self.driver = init_selenium_driver(headless=headless, data_dir_path=data_dir_path, proxy=proxy, user_agent=user_agent, headers=headers, allow_javascript=allow_javascript, disable_images=disable_images)
        self.headless = headless
        self.data_dir_path = data_dir_path
        self.is_ready = True
        self.proxy = proxy
        self.user_agent = user_agent
        self.headers = headers
        self.allow_javascript = allow_javascript
        self.disable_images = disable_images

    def close_driver(self):
        self.driver.close()
        self.is_ready = False

    def quit_driver(self):
        self.driver.quit()
        self.is_ready = False

    def reset_driver(self, proxy: str | None=None, user_agent: str | None=None, headers: dict | None=None, allow_javascript: bool | None = None, disable_images: bool | None = None):
        """ If possible quits the existing selenium driver and starts a new one
            Optionally a new proxy can be provided
        """
        try:
            delete_files_in_path(self.data_dir_path)
            self.quit_driver()
        except:
            pass
        allow_javascript = allow_javascript if allow_javascript != None else self.allow_javascript
        disable_images = disable_images if disable_images != None else self.disable_images
        self.driver = init_selenium_driver(headless=self.headless, data_dir_path=self.data_dir_path, proxy=proxy or self.proxy, user_agent=user_agent or self.user_agent, headers=headers or self.headers, allow_javascript=allow_javascript, disable_images=disable_images)
        if proxy:
            self.proxy = proxy
        if allow_javascript != None:
            self.allow_javascript = allow_javascript
        if disable_images != None:
            self.disable_images = disable_images
        self.is_ready = True

    def ensure_driver_is_alive(self):
        """If driver is not alive, reset driver"""
        if not is_webdriver_alive(self.driver):
            logging.info("Driver is not alive. Try to reset it...")
            self.reset_driver()
            assert is_webdriver_alive(self.driver)


def init_selenium_driver(headless=True, data_dir_path=None, proxy: str=None, user_agent: str | None = None, headers: dict | None=None, allow_javascript: bool = False, disable_images: bool = True) -> WebDriver:
    """Instantiate a WebDriver object (in this case, using Chrome)"""
    options = Options() #either firefox or chrome options

    # Performance increase by disable images and stylesheets
    # From https://stackoverflow.com/questions/49031428/how-to-disable-css-in-python-selenium-using-chromedriver-using-chromeoptions
    prefs = {'profile.default_content_setting_values': {'plugins': 2, 'popups': 2, 'geolocation': 2,
                                                        'notifications': 2, 'auto_select_certificate': 2,
                                                        'fullscreen': 2,
                                                        'mouselock': 2, 'mixed_script': 2, 'media_stream': 2,
                                                        'media_stream_mic': 2, 'media_stream_camera': 2,
                                                        'protocol_handlers': 2,
                                                        'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
                                                        'push_messaging': 2, 'ssl_cert_decisions': 2,
                                                        'metro_switch_to_desktop': 2,
                                                        'protected_media_identifier': 2, 'app_banner': 2,
                                                        'site_engagement': 2,
                                                        'durable_storage': 2}}
    if not allow_javascript:
        prefs['profile.default_content_setting_values']['javascript'] = 2
    if disable_images:
        prefs['profile.default_content_setting_values']['images'] = 2
    options.add_experimental_option('prefs', prefs)
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    # options.add_argument('--blink-settings=imagesEnabled=false')

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
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")

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
    driver = webdriver.Chrome(options=options, seleniumwire_options=seleniumwire_options)

    # def request_interceptor(request):
    #     for header_key, header_value in headers.items():
    #         if header_key == "user-agent":
    #             # Delete previous header
    #             try:
    #                 del request.headers[header_key]
    #             except Exception:
    #                 pass
    #             # Set new custom header
    #             request.headers[header_key] = header_value
    #
    # driver.request_interceptor = request_interceptor

    allowed_headers_to_change = ['user-agent', 'upgrade-insecure-requests', 'accept', 'sec-ch-ua', 'sec-ch-ua-mobile',
                                'sec-ch-ua-platform', 'sec-fetch-site', 'sec-fetch-mod', 'sec-fetch-user', 'accept-language'] #, ], 'accept-encoding']
    print("allowed_headers_to_change", allowed_headers_to_change)
    # ['upgrade-insecure-requests', 'user-agent', 'accept', 'sec-ch-ua', 'sec-ch-ua-mobile', 'sec-ch-ua-platform',
    #  'sec-fetch-site', 'sec-fetch-mod', 'sec-fetch-user', 'accept-encoding', 'accept-language']

    new_headers = {k: v for k, v in headers.items() if k in allowed_headers_to_change}
    driver.header_overrides = new_headers

    return driver

    #return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def is_webdriver_alive(driver: WebDriver) -> bool:
    """
    Check if the Selenium WebDriver is still operational.

    This function attempts to interact with the WebDriver by retrieving the current URL.
    If the WebDriver is responsive, the function returns True. If an exception occurs
    (e.g., WebDriverException), suggesting the WebDriver is no longer operational,
    the function returns False.

    Parameters:
    driver (selenium.webdriver): The WebDriver instance to be checked.

    Returns:
    bool: True if the WebDriver is still responsive, False otherwise.
    """
    try:
        # Attempt to get the current URL
        driver.current_url
        return True
    except WebDriverException:
        return False
    except Exception as e:
        logging.warning(f"Got some undetected exception {e}")
        return False

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

def get_full_page_screenshot(driver: WebDriver, by_name=By.TAG_NAME, by_value="body") -> bytes:
    """Enhance window size to get full page screenshot"""
    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    # driver.save_screenshot(path)  # has scrollbar
    screenshot_as_png = driver.find_element(by_name, by_value).screenshot_as_png
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