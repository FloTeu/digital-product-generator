import requests
import tempfile
import streamlit as st


from io import BytesIO
from PIL import Image
from digiprod_gen.backend.data_classes import CrawlingMBARequest


@st.cache_data
def image_url2image_bytes_io(image_url: str) -> BytesIO:
    response = requests.get(image_url)
    return BytesIO(response.content)


def send_mba_overview_request(request: CrawlingMBARequest, **kwargs):
    response = requests.get(
        url=request.mba_overview_url,
        headers=request.headers,
        proxies = {
            "http": request.proxy,
            "https": request.proxy
        },
        **kwargs
    )
    return response

def save_img_to_memory(image_pil: Image) -> str:
    # Create a temporary file to store the image
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        # Save the image data to the temporary file
        image_pil.save(tmp_file, format='png')
        
        # Retrieve the path to the temporary file
        tmp_file_path = tmp_file.name

    return tmp_file_path