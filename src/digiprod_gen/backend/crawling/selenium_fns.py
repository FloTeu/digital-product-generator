import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager


# TODO: multiple users would potentially use the same browser. This might lead to bot detection trigger 
@st.cache_resource
def init_selenium_driver(headless=True) -> WebDriver:
    """Instantiate a WebDriver object (in this case, using Chrome)"""
    options = Options() #either firefox or chrome options
    options.add_argument('--disable-gpu')
    if headless:
        options.add_argument('--headless')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def close_selenium_driver(driver: WebDriver):
    driver.quit()