import os
import time
from selenium.webdriver.chrome.webdriver import WebDriver
#from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import FirefoxOptions
import tempfile
from digiprod_gen.backend.data_classes.mba import MBAMarketplaceDomain
from digiprod_gen.backend.io.io_fns import save_img_to_memory
from digiprod_gen.backend.data_classes.mba import MBAProductCategory
from digiprod_gen.backend.transform.transform_fns import mba_product_category2html_row_name
from PIL import Image
from typing import List


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

def authenticate_mba_with_opt_code(driver: WebDriver, second_factor_code: str):
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

def click_on_create_new(driver):
    # find the link element by its text content
    link_element = driver.find_element("link text", "Create")
    # click on the link
    link_element.click()

def select_products_and_marketplaces(driver, products: List[MBAProductCategory], marketplaces: List[MBAMarketplaceDomain]):
    """Selects desired products and target marketplaces in MBA upload/create menu"""
    # open selecton menu
    select_products_button = driver.find_element(By.ID, "select-marketplace-button")
    select_products_button.click()

    # extract the marketplaces from the html header row
    header_row = driver.find_element("xpath", '//tbody/tr[1]')
    marketplace_header = [h.accessible_name for h in header_row.find_elements("xpath", './*')[1:]]

    # clear all products and marketplaces
    driver.find_element(By.ID, "select-none").click()

    table = driver.find_element(By.CLASS_NAME, "select-products-table")
    # Loop through the products
    for product in products:
        # get html row of product
        mba_html_product = mba_product_category2html_row_name(product)
        row = table.find_element("xpath", f".//tr[contains(td, '{mba_html_product}')]")

        for marketplace in marketplaces:
            # get index of markeplace header which identicates column
            marketplace_index = next((i for i, s in enumerate(marketplace_header) if marketplace in s), None)
            # click on product marketplace cell
            # Note 0 is the product colum therefore we start with 1
            row.find_elements("xpath", ".//td")[1 + marketplace_index].click()

    # Find the submit button by its ID (replace "submit-button-id" with the actual ID of the button)
    submit_button = driver.find_element(By.CLASS_NAME, "btn-submit")

    # Click the submit button
    submit_button.click()

def upload_image(driver, image_pil: Image):
    # store image to temp memory
    temp_file_path = save_img_to_memory(image_pil)
    # find the image upload input element by its text content
    choose_file = driver.find_element(By.CLASS_NAME, "file-upload-input")
    # sen image data
    choose_file.send_keys(temp_file_path)
    # wait until file is uploaded to server
    time.sleep(2)
    # delete file again
    os.remove(temp_file_path)

def insert_listing_text(driver, title: str, brand: str, bullet_1: str, bullet_2: str, description: str | None = None):
    """Inserts all mba listings i.e. Text, Brand, bullets and description"""
    # Get input objects
    title_input = driver.find_element(By.ID, "designCreator-productEditor-title")
    brand_input = driver.find_element(By.ID, "designCreator-productEditor-brandName")
    bullet_one_input = driver.find_element(By.ID, "designCreator-productEditor-featureBullet1")
    bullet_two_input = driver.find_element(By.ID, "designCreator-productEditor-featureBullet2")
    description_input = driver.find_element(By.ID, "designCreator-productEditor-description")

    # clear forms
    title_input.clear()
    brand_input.clear()
    bullet_one_input.clear()
    bullet_two_input.clear()
    description_input.clear()
    
    # fill data
    title_input.send_keys(title)
    brand_input.send_keys(brand)
    bullet_one_input.send_keys(bullet_1)
    bullet_two_input.send_keys(bullet_2)
    if description:
        description_input.send_keys(description)

def publish_to_mba(driver, searchable=True):
    # make sure product is public for everyone
    if searchable:
        driver.find_element(By.XPATH, "//*[contains(text(), 'Searchable')]").find_element(By.NAME, "isDiscoverable").click()
    else:
        driver.find_element(By.XPATH, "//*[contains(text(), 'Non-searchable')]").find_element(By.NAME, "isDiscoverable").click()
    driver.find_element(By.ID, "submit-button").click()

    
    