import requests
import streamlit as st


from io import BytesIO

from digiprod_gen.backend.data_classes import CrawlingMBARequest


@st.cache_data
def image_url2image_bytes_io(image_url: str) -> BytesIO:
    response = requests.get(image_url)
    return BytesIO(response.content)


def send_mba_overview_request(request: CrawlingMBARequest):
    response = requests.get(
        url=request.mba_overview_url,
        headers=request.headers,
        proxies = {
            "http": request.proxy,
            "https": request.proxy
        }
    )
    return response


