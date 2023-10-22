import streamlit as st
import httpx

from fastapi.testclient import TestClient
from digiprod_gen.backend_api.models.config import BackendConfig
from digiprod_gen.backend_api.api.api import app

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


    def post(self, endpoint: str, **kwargs) -> httpx.Response:
        """Executes a backend post call"""
        if self.config.debug:
            try:
                return self.test_client.post(endpoint, **kwargs)
            except Exception as e:
                st.error(f"Backend API failed {e}")
                return httpx.Response(status_code=500, text=str(e))
        else:
            # TODO: implement code for deployed call
            raise NotImplementedError
