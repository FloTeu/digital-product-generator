import re
from typing import List
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from digiprod_gen.backend.models.mba import MBAProduct, MBAMarketplaceDomain
from digiprod_gen.backend.browser.selenium_fns import has_element_with_class, html2file
from digiprod_gen.backend.browser.crawling.utils.utils_mba import is_product_feature_listing
from digiprod_gen.backend.utils.exceptions import HtmlHasChangedException



def get_mba_product_web_elements(driver: WebDriver) -> List[WebElement]:
    """Returns a list of selenium web elements containing valid mba products"""
    product_elements = driver.find_elements(By.XPATH, "//div[@class='sg-col-inner']")
    # ignore products which are no utils product or sponsored products
    return [p for p in product_elements if is_mba_product(p) and not has_element_with_class(p, "sponsored-brand-label-info-desktop")]


def extract_mba_products(mba_product_elements: List[WebElement], marketplace: MBAMarketplaceDomain) -> List[MBAProduct]:
    """Extracts MBAProduct objects out of utils overview page"""
    mba_products: List[MBAProduct] = []
    for product_element in mba_product_elements:
        mba_product: MBAProduct = overview_product_element2mba_product(product_element, marketplace=marketplace)
        mba_products.append(mba_product)

    if len(mba_product_elements) == 0:
        raise ValueError(f"No mba products could be found")
    elif len(mba_products) == 0 and len(mba_product_elements) > 0:
        raise ValueError(f"{len(mba_product_elements)} products found. But no product could be extracted")

    return mba_products


def overview_product_element2mba_product(product_element: WebElement, marketplace: MBAMarketplaceDomain) -> MBAProduct:
    asin = overview_product_get_asin(product_element)
    product_url = f"https://www.amazon.{marketplace}/dp/{asin}"
    try:
        price = overview_product_get_price(product_element)
    except:
        price = None
    # TODO: Try to get brand in detail page crawling
    try:
        brand = overview_product_get_brand(product_element)
    except:
        brand = None
    return MBAProduct(
        asin = asin,
        title = overview_product_get_title(product_element),
        image_url = overview_product_get_image_url(product_element),
        product_url = product_url,
        brand=brand,
        price=price,
        #bullets=[],
        description=None,
        marketplace=marketplace
      )

def extend_mba_product(mba_product: MBAProduct, driver: WebDriver) -> MBAProduct:
    marketplace: MBAMarketplaceDomain = mba_product.marketplace
    bullets = product_get_bullets(driver)
    mba_product.bullets = [b for b in bullets if is_product_feature_listing(marketplace, b)]
    try:
        mba_product.description = product_get_description(driver)
    except:
        pass
    try:
        mba_product.price = product_get_price(driver)
    except:
        pass
    if not mba_product.brand:
        try:
            mba_product.brand = product_get_brand(driver)
        except:
            pass

    return mba_product


'''
### Parser Functions (overview page)
'''


def overview_product_get_asin(product_element: WebElement) -> str:
    parent_element = product_element.find_element(By.XPATH, '..')  # Get the parent element
    return parent_element.get_attribute("data-asin").strip()

def overview_product_get_image_url(product_element: WebElement) -> str:
    image_element = product_element.find_element(By.CLASS_NAME, "s-image")
    return image_element.get_attribute("src")

def overview_product_get_brand(product_element: WebElement) -> str | None:
    h2_elements_with_class = product_element.find_elements(By.XPATH, ".//h2[contains(@class, 'a-size-mini')]")
    for h2_element in h2_elements_with_class:
        # Brand tag is the one which contains no "a" tag
        if not h2_element.find_elements(By.TAG_NAME, "a"):
            return h2_element.text.strip()

def overview_product_get_title_section_tag(product_element: WebElement) -> WebElement:
    h2_elements_with_class = product_element.find_elements(By.XPATH, ".//h2[contains(@class, 'a-size-mini')]")
    for h2_element in h2_elements_with_class:
        # Title tag is the one which contains an "a" tag
        if h2_element.find_elements(By.TAG_NAME, "a"):
            return h2_element

def overview_product_get_title(product_element: WebElement) -> str:
    title_section_element = overview_product_get_title_section_tag(product_element)
    return title_section_element.text.strip()

def overview_product_get_product_url(product_element: WebElement) -> str:
    # TODO: Seems like this parsing function does not work like before with bs4
    title_section_element = overview_product_get_title_section_tag(product_element)
    product_link = title_section_element.find_element(By.TAG_NAME, "a")
    return product_link.get_attribute("href")

def overview_product_get_price(product_element: WebElement) -> str:
    # Catch case COM marketplace
    price_whole_elements = product_element.find_elements(By.CLASS_NAME, "a-price-whole")
    price_fraction_elements = product_element.find_elements(By.CLASS_NAME, "a-price-fraction")

    if len(price_fraction_elements) > 0:
        price_str = (price_whole_elements[0].text.strip() + "." +
                     price_fraction_elements[0].text.strip())
    else:
        price_str = price_whole_elements[0].text.strip()

    return price_str2price(price_str)


'''
### Parser Functions (product page)
'''


def product_get_price(element: WebElement | WebDriver):
    price_str = element.find_element(By.XPATH, ".//div[@id='centerCol']//span[@class='a-price']//span").text
    return price_str2price(price_str)


def product_get_bullets(element: WebDriver) -> List[str]:
    # get parent of first element with class "product-facts-title" and extract all li elements
    if "feature-bullets" in element.page_source:
        li_elements = element.find_elements(By.XPATH, "//*[contains(@id, 'feature-bullets')][1]//li")
    elif "product-facts-title" in element.page_source:
        li_elements = element.find_elements(By.XPATH, "//*[contains(@class, 'product-facts-title')][1]/parent::*//li")
    else:
        raise HtmlHasChangedException()
    return [bullet.text.strip() for bullet in li_elements]


def product_get_description(element: WebElement | WebDriver) -> str:
    return element.find_element(By.XPATH, ".//div[@id='productDescription']").text.strip()


def product_get_brand(element: WebElement | WebDriver) -> str:
    return element.find_element(By.XPATH, ".//a[@id='bylineInfo']").text.strip()


'''
### Helper Functions
'''



def price_str2price(price_str: str) -> float:
    return float(re.findall("\d+\.\d+", price_str.replace(",", "."))[0])

def is_mba_product(product_element: WebElement) -> bool:
    """product is considered as utils product if it contains a asin id"""
    try:
        asin = overview_product_get_asin(product_element)
        return True
    except:
        return False