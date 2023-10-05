import streamlit as st
from typing import Any

from fastapi.testclient import TestClient
from digiprod_gen.backend.data_classes.config import BackendConfig
from digiprod_gen.backend_api.api import app

class BackendCaller:
    """Gateway between frontend and backend"""
    def __init__(self, config: BackendConfig):
        self.config = config
        self.base_url = f"{config.host}:{config.port}"
        if self.config.debug:
            self.test_client = TestClient(app)

    def get(self, endpoint: str) -> Any:
        """Executes a backend get call"""
        if self.config.debug:
            return self.test_client.get(endpoint)
        else:
            # TODO: implement code for deployed call
            raise NotImplementedError


    def post(self, endpoint: str, **kwargs) -> Any:
        """Executes a backend post call"""
        if self.config.debug:
            try:
                return self.test_client.post(endpoint, json=kwargs)
            except Exception as e:
                st.error(str(e))
        else:
            # TODO: implement code for deployed call
            raise NotImplementedError
