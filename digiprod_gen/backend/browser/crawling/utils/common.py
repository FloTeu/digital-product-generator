import random
from typing import List

import requests
import streamlit as st


def get_headers_list() -> List[str]:
    response = requests.get('http://headers.scrapeops.io/v1/browser-headers?api_key=' + st.secrets["api_token"]["scrape_ops"])
    json_response = response.json()
    return json_response.get('result', [])


def get_user_agent_list() -> List[str]:
  response = requests.get('http://headers.scrapeops.io/v1/user-agents?api_key=' + st.secrets["api_token"]["scrape_ops"])
  json_response = response.json()
  return json_response.get('result', [])


def get_random_user_agent():
    user_agent_list = get_user_agent_list()
    return random.choice(user_agent_list)

def get_random_headers():
    headers_list = get_headers_list()
    return random.choice(headers_list)