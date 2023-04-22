import random
import numpy as np
from typing import List
from digiprod_gen.backend.crawling import parser


from bs4.element import Tag

from digiprod_gen.backend.crawling.mba import url_creator
from digiprod_gen.backend.crawling.utils import get_headers_list
from digiprod_gen.backend.data_classes import MBAMarketplaceDomain, MBAProductCategory


def is_mba_product(product_tag: Tag) -> bool:
    """product is considered as mba product if it contains a asin id"""
    try:
        asin = parser.overview_product_get_asin(product_tag)
        return True
    except:
        return False


def get_mba_overview_urls(marketplace: MBAMarketplaceDomain, product_category: MBAProductCategory, search_term: str, start_page=0, number_pages=1) -> List[str]:
    """Returns a List of urls of mba overview pages"""
    urls_mba = []
    url_mba = url_creator.main([search_term, marketplace.value, product_category.value, "best_seller"])

    # if start_page is other than one, crawler should start from differnt page
    until_page = 401

    if number_pages != 0:
        until_page = start_page + number_pages
    for page_number in np.arange(start_page, until_page, 1):
        if page_number <= 400:
            url_mba_page = url_mba + "&page=" + str(page_number)  # +"&ref=sr_pg_"+str(page_number)
            urls_mba.append(url_mba_page)
    return urls_mba


def get_accept_language(marketplace: MBAMarketplaceDomain):
    if marketplace == MBAMarketplaceDomain.COM:
        return 'en-US;q=0.8,en;q=0.7'
    elif marketplace == MBAMarketplaceDomain.DE:
        return 'de-DE,DE;q=0.9;q=0.7'
    else:
        raise NotImplementedError


def get_random_headers(marketplace: MBAMarketplaceDomain) -> dict:
    headers_list = get_headers_list()
    headers = random.choice(headers_list)
    headers["Host"] = 'www.amazon.' + marketplace
    headers["authority"] = 'www.amazon.' + marketplace
    headers["accept-language"] = get_accept_language(marketplace)
    return headers


def is_product_feature_listing(marketplace: MBAMarketplaceDomain, product_feature):
    """If one bullet point/ product feature is a listing created by user (contains relevant keywords)"""
    if marketplace in [MBAMarketplaceDomain.COM, MBAMarketplaceDomain.UK]:
        return (not any(indicator in product_feature.lower() for indicator in
               ["solid color", "imported", "lightweight", "cotton", "classic fit", "classic cut", "double-stitched", "half sleeve", "closure:", "pull on", "machine wash"])) and len(product_feature) >= 10
    elif marketplace == MBAMarketplaceDomain.DE:
        return (not any(indicator in product_feature.lower() for indicator in
               ["unifarben", "baumwolle", "klassisch geschnitten", "doppelt genäht", "pflegehinweis", "polyester", "grau meliert", "halbarm", "verschluss:", "maschinenwäsche", "leicht, klassische", "kurzarm"])) and len(product_feature) >= 10
    else:
        raise ValueError("Not defined for marketplace %s" % marketplace)