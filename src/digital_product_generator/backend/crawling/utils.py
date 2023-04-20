import random
import numpy as np
import streamlit as st
from typing import List
import requests

from ..data_classes import MBAMarketplaceDomain, MBAProductCategory
from . import url_creator

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

def get_headers_list():
    response = requests.get('http://headers.scrapeops.io/v1/browser-headers?api_key=' + st.secrets["scrape_ops_api_key"])
    json_response = response.json()
    return json_response.get('result', [])

def get_random_headers(marketplace: MBAMarketplaceDomain) -> dict:
    headers_list = get_headers_list()
    headers = random.choice(headers_list)
    headers["Host"] = 'www.amazon.' + marketplace
    headers["authority"] = 'www.amazon.' + marketplace
    headers["accept-language"] = get_accept_language(marketplace)
    return headers

def get_user_agent_list():
  response = requests.get('http://headers.scrapeops.io/v1/user-agents?api_key=' + st.secrets["scrape_ops_api_key"])
  json_response = response.json()
  return json_response.get('result', [])

def get_random_user_agent():
    user_agent_list = get_user_agent_list()
    return random.choice(user_agent_list)

def get_accept_language(marketplace: MBAMarketplaceDomain):
    if marketplace == "com":
        return 'en-US;q=0.8,en;q=0.7'
    elif marketplace == "de":
        return 'de-DE,DE;q=0.9;q=0.7'
    else:
        return 'en-US;q=0.8,en;q=0.7'


def is_product_feature_listing(marketplace: MBAMarketplaceDomain, product_feature):
    """If one bullet point/ product feature is a listing created by user (contains relevant keywords)"""
    if marketplace in ["com","co.uk"]:
        return (not any(indicator in product_feature.lower() for indicator in
               ["solid color", "imported", "lightweight", "cotton", "classic fit", "classic cut", "double-stitched", "half sleeve", "closure:", "pull on", "machine wash"])) and len(product_feature) >= 10
    elif marketplace == "de":
        return (not any(indicator in product_feature.lower() for indicator in
               ["unifarben", "baumwolle", "klassisch geschnitten", "doppelt genäht", "pflegehinweis", "polyester", "grau meliert", "halbarm", "verschluss:", "maschinenwäsche", "leicht, klassische", "kurzarm"])) and len(product_feature) >= 10
    else:
        raise ValueError("Not defined for marketplace %s" % marketplace)