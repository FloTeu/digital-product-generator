import streamlit as st
import httpx

from fastapi.testclient import TestClient
from digiprod_gen.backend.models.config import BackendConfig
from digiprod_gen.backend.api.api import app
from digiprod_gen.backend.image.conversion import pil2bytes_io
from PIL import Image

class BackendCaller:
    """Gateway between frontend and backend
        Unusual behavior: Errors during backend call are catched and displayed in frontend as error message
    """
    def __init__(self, config: BackendConfig):
        self.config = config
        self.base_url = f"{config.host}:{config.port}"
        if self.config.debug:
            self.test_client = TestClient(app)

    def get(self, endpoint: str, **kwargs) -> httpx.Response:
        """Executes a backend get call"""
        if self.config.debug:
            try:
                return self.test_client.get(endpoint, **kwargs)
            except Exception as e:
                st.error(f"Backend API failed {e}")
                return httpx.Response(status_code=500, text=str(e))
        else:
            # TODO: implement code for deployed call
            raise NotImplementedError


    def post(self, endpoint: str, img_pil: Image = None, **kwargs) -> httpx.Response:
        """Executes a backend post call"""
        files = self.img_pil2files(img_pil) if img_pil else None
        if self.config.debug:
            try:
                return self.test_client.post(endpoint, files=files, **kwargs)
            except Exception as e:
                st.error(f"Backend API failed {e}")
                return httpx.Response(status_code=500, text=str(e))
        else:
            # TODO: implement code for deployed call
            raise NotImplementedError

    def img_pil2files(self, img_pil: Image):
        """Transforms a pillow image to valid format for http request
        Assumption: Endpoint must define file as image_file
        """
        image_byte_array = pil2bytes_io(img_pil)
        return {
            "image_file": ("image_file.png", image_byte_array, 'image/png')
        }
