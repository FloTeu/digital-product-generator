import os
import time
import uuid
import logging

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException

from digiprod_gen.backend.browser.selenium_fns import hover_over_element, wait_until_element_exists, SeleniumBrowser
from digiprod_gen.backend.browser import selenium_fns
from digiprod_gen.backend.models.mba import MBAMarketplaceDomain, MBAProductFitType, MBAProductCategory, MBAProductColor
from digiprod_gen.backend.etl.transform_fns import mba_product_category2html_row_name
from PIL import Image
from typing import List


def login_mba(driver: WebDriver, email: str, password: str):
    """Fill utils login form and simulate submit button click"""
    # Fill in the form fields
    print("Try to provide utils email and password")
    username_input = driver.find_element(By.ID, "ap_email")
    password_input = driver.find_element(By.ID, "ap_password")
    username_input.send_keys(email)
    password_input.send_keys(password)

    # Submit the form
    submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    submit_button.click()

def authenticate_mba_with_opt_code(driver: WebDriver, second_factor_code: str):
    """Fill utils second factor authentification form and simulate submit button click"""
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

def open_dashboard(driver, max_time_wait: int = 3):
    driver.get("https://merch.amazon.com/dashboard")
    wait_until_dashboard_is_ready(driver, max_time_wait=max_time_wait)

def open_create_new(driver):
    # find the link element by its text content
    driver.get("https://merch.amazon.com/designs/new")

def select_products_and_marketplaces(driver, products: List[MBAProductCategory], marketplaces: List[MBAMarketplaceDomain]):
    """Selects desired products and target marketplaces in MBA upload/create menu"""
    # TODO: Pillow product is not selected at the moment
    # open selection menu
    try:
        select_products_button = driver.find_element(By.ID, "select-marketplace-button")
    except Exception as e:
        select_products_button = driver.find_element(By.ID, "select-marketplace-button-original")
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
            product_marketplace_checkbox: List[WebElement] = row.find_elements("xpath", ".//td")[1 + marketplace_index].find_elements(By.TAG_NAME, 'i')
            if product_marketplace_checkbox:
                product_marketplace_checkbox[0].click()

    # Find the submit button by its ID (replace "submit-button-id" with the actual ID of the button)
    submit_button = driver.find_element(By.CLASS_NAME, "btn-submit")

    # Click the submit button
    submit_button.click()

def iterate_over_product_cards(driver: WebDriver, product_categories: List[MBAProductCategory], editor_change_fn, **kwargs):
    products_cards = driver.find_elements(By.CLASS_NAME, "product-card")
    selected_product_cat_names = [mba_product_category2html_row_name(product) for product in product_categories]
    for products_card in products_cards:
        product_name = products_card.find_element(By.CLASS_NAME, "heading").text
        if product_name not in selected_product_cat_names:
            continue
        print(product_name)
        # open edit menu
        try:
            products_card.find_element(By.CLASS_NAME, "card-button").click()
        except (NoSuchElementException, ElementClickInterceptedException) as e:
            # if edit button not clickable the desired product category might not be selected correctly
            continue

        product_editor = wait_until_element_exists(driver, "//*[contains(@class, 'product-editor')]")
        editor_change_fn(product_editor, **kwargs)


def select_fit_types_in_product_editor(product_editor, fit_types: List[MBAProductFitType]):
    """Selects desired fit types in MBA upload/create menu"""
    try:
        product_editor_fit_types = product_editor.find_element(By.CLASS_NAME, "fit-type-container")
    except NoSuchElementException as e:
        # if fit type container is not available we skip this product
        return None

    # Click Men fit type
    men_checkbox = product_editor_fit_types.find_element(By.CSS_SELECTOR, '.men-checkbox input[type="checkbox"]')
    is_checked = men_checkbox.get_attribute('checked') == 'true'
    if (is_checked and MBAProductFitType.MEN not in fit_types) or (not is_checked and MBAProductFitType.MEN in fit_types):
        try:
            men_checkbox.find_element(By.XPATH, 'preceding-sibling::node()').click()
        except (ElementClickInterceptedException) as e:
            men_checkbox.find_element(By.XPATH, 'following-sibling::i').click()

    # Click Women fit type
    women_checkbox = product_editor_fit_types.find_element(By.CSS_SELECTOR, '.women-checkbox input[type="checkbox"]')
    is_checked = women_checkbox.get_attribute('checked') == 'true'
    if (is_checked and MBAProductFitType.WOMAN not in fit_types) or (not is_checked and MBAProductFitType.WOMAN in fit_types):
        try:
            women_checkbox.find_element(By.XPATH, 'preceding-sibling::node()').click()
        except (ElementClickInterceptedException) as e:
            women_checkbox.find_element(By.XPATH, 'following-sibling::i').click()

    # TODO: Selecting youth sice does not work sometimes.
    # Click Youth fit type
    try:
        youth_checkbox = product_editor_fit_types.find_element(By.CSS_SELECTOR, '.youth-checkbox input[type="checkbox"]')
        is_checked = youth_checkbox.get_attribute('checked') == 'true'
    except Exception:
        # Can happen if youth size is not available, e.g. for fit type tank top
        logging.warning("Could not find youth checkbox")
        return None
    if (is_checked and MBAProductFitType.YOUTH not in fit_types) or (not is_checked and MBAProductFitType.YOUTH in fit_types):
        try:
            youth_checkbox.find_element(By.XPATH, 'preceding-sibling::node()').click()
        except (ElementClickInterceptedException) as e:
            # second try
            youth_checkbox.find_element(By.XPATH, 'following-sibling::i').click()
        except (StaleElementReferenceException, NoSuchElementException) as e:
            # if youth size is not available we skip this product as men and women
            pass

def select_colors_in_product_editor(product_editor, colors: List[MBAProductColor], web_driver):
    """Selects desired colors in MBA upload/create menu for one product editor"""
    try:
        product_editor_color_checkboxes = product_editor.find_elements(By.CLASS_NAME, "color-checkbox-container")
    except NoSuchElementException as e:
        # if fit type container is not available we skip this product
        return None

    for i, product_editor_color_checkbox in enumerate(product_editor_color_checkboxes):
        # get checkbox element
        try:
            color_checkbox = product_editor_color_checkbox.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
        except StaleElementReferenceException as e:
            print("Could not get color checkbox element")
            try:
                product_editor_color_checkbox = product_editor.find_elements(By.CLASS_NAME, "color-checkbox-container")[i]
                color_checkbox = product_editor_color_checkbox.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
            except StaleElementReferenceException as e:
                continue
            #break

        is_checked = color_checkbox.get_attribute('checked') == 'true'
        # extract color name
        hover_over_element(web_driver, product_editor_color_checkbox)
        color_tooltip = wait_until_element_exists(web_driver, "//*[contains(@class, 'tooltip')]", timeout=1)
        if color_tooltip == None:
            # TODO: How to handle this case?
            continue
        # catch products like raglan with color name "Black/Heather Grey"
        color_name = color_tooltip.text.split("/")[0]
        if (is_checked and color_name not in colors) or (not is_checked and color_name in colors):
            # Click color checkbox
            product_editor_color_checkbox.click()


def select_fit_types(driver: WebDriver, product_categories: List[MBAProductCategory], fit_types: List[MBAProductFitType]):
    """Selects desired fit types in MBA upload/create menu"""
    iterate_over_product_cards(driver, product_categories=product_categories, editor_change_fn=select_fit_types_in_product_editor, fit_types=fit_types)


def select_colors(driver: WebDriver, product_categories: List[MBAProductCategory], colors: List[MBAProductColor]):
    """Selects desired fit types in MBA upload/create menu"""
    iterate_over_product_cards(driver, product_categories=product_categories, editor_change_fn=select_colors_in_product_editor, colors=colors, web_driver=driver)


def upload_image(browser: SeleniumBrowser, image_pil: Image):
    driver = browser.driver
    temp_file_path = f"{browser.data_dir_path}/{uuid.uuid4().hex}.png"
    image_pil.save(temp_file_path, format='png')
    time.sleep(1)
    # # store image to temp memory
    # temp_file_path = save_img_to_memory(image_pil)
    # find the image upload input element by its text content
    choose_file = driver.find_element(By.CLASS_NAME, "file-upload-input")
    # sen image data
    choose_file.send_keys(temp_file_path)
    # wait until file is uploaded to server
    time.sleep(4)
    # delete file again
    os.remove(temp_file_path)

def insert_listing_text(driver, title: str, brand: str, bullet_1: str | None = None, bullet_2: str | None = None, description: str | None = None):
    """Inserts all utils listings i.e. Text, Brand, bullets and description"""
    # Get input objects
    title_input = driver.find_element(By.ID, "designCreator-productEditor-title")
    brand_input = driver.find_element(By.ID, "designCreator-productEditor-brandName")
    bullet_one_input = driver.find_element(By.ID, "designCreator-productEditor-featureBullet1")
    bullet_two_input = driver.find_element(By.ID, "designCreator-productEditor-featureBullet2")
    description_input = driver.find_element(By.ID, "designCreator-productEditor-description")

    # clear forms
    driver.execute_script("arguments[0].value = '';", title_input)
    driver.execute_script("arguments[0].value = '';", brand_input)
    driver.execute_script("arguments[0].value = '';", bullet_one_input)
    driver.execute_script("arguments[0].value = '';", bullet_two_input)
    driver.execute_script("arguments[0].value = '';", description_input)

    # fill data
    title_input.send_keys(title)
    brand_input.send_keys(brand)
    if bullet_1:
        bullet_one_input.send_keys(bullet_1)
    if bullet_2:
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
    publish_submit_button = wait_until_element_exists(driver, "//*[contains(@class, 'btn-submit')]", timeout=3)
    publish_submit_button.click()

def change_language_to_en(driver: WebDriver, language_url="/switch-locale?language=en_US"):
    globe_icon = wait_until_element_exists(driver, "//*[contains(@class, 'globe-icon')]")
    globe_icon.click()
    driver.find_element(By.XPATH, f"//a[@href='{language_url}']").click()

def remove_uploaded_image(driver: WebDriver, xpath: str):
    try:
        delete_image_i_tag = driver.find_element(By.XPATH, xpath)
        # Element must be in focus in order to be clickable
        selenium_fns.focus_element(driver, delete_image_i_tag)
        selenium_fns.scroll_page(driver, -300)
        selenium_fns.scroll_to_top_left(driver)
        delete_image_i_tag.click()

    except (NoSuchElementException, ElementClickInterceptedException) as e:
        print("Exception", str(e))
        pass