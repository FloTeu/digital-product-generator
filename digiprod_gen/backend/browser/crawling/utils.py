import random
import streamlit as st
import requests
from typing import List


#@st.cache_data
def get_headers_list() -> List[str]:
    response = requests.get('http://headers.scrapeops.io/v1/browser-headers?api_key=' + st.secrets["api_token"]["scrape_ops"])
    json_response = response.json()
    return json_response.get('result', [])

#@st.cache_data
def get_user_agent_list() -> List[str]:
  response = requests.get('http://headers.scrapeops.io/v1/user-agents?api_key=' + st.secrets["api_token"]["scrape_ops"])
  json_response = response.json()
  return json_response.get('result', [])

def get_random_user_agent():
    user_agent_list = get_user_agent_list()
    return random.choice(user_agent_list)

