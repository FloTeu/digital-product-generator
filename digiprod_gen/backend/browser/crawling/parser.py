import re
from typing import List
from bs4.element import Tag

def price_str2price(price_str: str) -> float:
    return float(re.findall("\d+\.\d+", price_str.replace(",", "."))[0])


"""
Parse for overview page
"""
def overview_product_get_asin(product_tag: Tag) -> str:
    return product_tag.parent.attrs["data-asin"].strip()

def overview_product_get_image_url(product_tag: Tag) -> str:
    return product_tag.find_next("img", {"class": "s-image"}).attrs["src"]

def overview_product_get_brand(product_tag: Tag) -> str:
    return product_tag.find_next("h5").text.strip()

def overview_product_get_title_section_tag(product_tag: Tag) -> Tag:
    return product_tag.find_next("h2", {"class": ["a-size-mini"]})

def overview_product_get_title(product_tag: Tag) -> str:
    return overview_product_get_title_section_tag(product_tag).find_next("span").text.strip()

def overview_product_get_product_url(product_tag: Tag) -> str:
    return overview_product_get_title_section_tag(product_tag).find_next("a").attrs["href"]

def overview_product_get_price(product_tag: Tag) -> str:
    # catch case COM marketplace
    if len(product_tag.find_all("span", {"class": "a-price-fraction"})) > 0:
        price_str = (product_tag.find_all("span", {"class": "a-price-whole"})[0].text.strip() + "." +
                    product_tag.find_all("span", {"class": "a-price-fraction"})[0].text.strip())
    else:
       price_str = product_tag.find_all("span", {"class": "a-price-whole"})[0].text.strip()
    return price_str2price(price_str)

"""
Parser for product page
"""
def get_price(product_tag: Tag) -> float:
    price_str = product_tag.find_all("div", {"id": "centerCol"})[0].find_next("span", {"class": "a-price"}).find_next("span").text
    return price_str2price(price_str)

def get_bullets(product_tag: Tag) -> List[str]:
    try:
        return [bullet.text.strip() for bullet in product_tag.find_all("div", {"id": "feature-bullets"})[0].find_all("li")]
    except:
        return [bullet.text.strip() for bullet in product_tag.find_all("div", {"id": "productFactsExpander"})[0].find_all("li")]


def get_description(product_tag: Tag) -> str:
    return product_tag.find_all("div", {"id": "productDescription"})[0].text.strip()


def get_brand(product_tag: Tag) -> str:
    return product_tag.find_all("a", {"id": "bylineInfo"})[0].text.strip()

