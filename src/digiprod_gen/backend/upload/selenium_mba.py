from selenium import webdriver
#from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import FirefoxOptions


def init_selenium_driver() -> WebDriver:
    """Instantiate a WebDriver object (in this case, using Chrome)"""
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    return webdriver.Firefox(options=opts)

def close_selenium_driver(driver: WebDriver):
    driver.quit()


def login_mba(driver: WebDriver, email: str, password: str):
    """Fill mba login form and simulate submit button click"""
    # Fill in the form fields
    username_input = driver.find_element(By.NAME, "email")
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys(email)
    password_input.send_keys(password)

    # Submit the form
    submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    submit_button.click()

#2FA
#second_factor_code = st.sidebar.number_input("2FA Code:")

def authenticate_mba_with_opt_code(driver: WebDriver, second_factor_code: int):
    """Fill mba second factor authentification form and simulate submit button click"""
    otp_code = driver.find_element(By.NAME, "otpCode")
    remember_device = driver.find_element(By.NAME, "rememberDevice")
    otp_code.send_keys(second_factor_code)
    remember_device.click()

    # Submit the form
    submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    submit_button.click()

def wait_until_dashboard_is_ready(driver: WebDriver, max_time_wait: int = 3):
    """ Wait for the spinner to disappear and the page to finish rendering"""
    wait = WebDriverWait(driver, max_time_wait)
    try:
        spinner = wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "app-loading")))
        tier_element_list = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'card')))
        print("Page is ready!")
        return tier_element_list
    except TimeoutException:
        print("Loading took too much time!")

