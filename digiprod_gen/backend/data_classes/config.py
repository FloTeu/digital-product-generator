from pathlib import Path
from typing import List

from pydantic import BaseModel, validator, Field
from digiprod_gen.backend_api.models.mba import MBAMarketplaceDomain

class DigiProdGenBrowserConfig(BaseModel):
    selenium_data_dir_path: Path

    @validator("selenium_data_dir_path", allow_reuse=True)
    def validate_selenium_data_dir_path(cls, data_dir_path):
        # create dir if not exists
        data_dir_path.mkdir(parents=True, exist_ok=True)
        return data_dir_path

class DigiProdGenMBAMarketplaceConfig(BaseModel):
    marketplace: MBAMarketplaceDomain = Field(description="mba marketplace domain")
    postcode: str = Field(description="Valid example postcode of the main country in which the marketplace operates")
    proxy: str | None = Field(description="Crawling proxy which should be used to get better response by mba server")
    proxy_port: int | None = Field(description="Port on which the proxy can be accessed")
    proxy_socks: str | None = Field(description="Optional SOCKS to hide ip address")


    def get_proxy_with_secrets(self, user_name, password) -> str | None:
        """If proxy exists, return proxy url with secrets. Otherwise None"""
        if self.proxy and "perfect-privacy.com" in self.proxy:
            return f"http://{user_name}:{password}@{self.proxy}:{self.proxy_port}"
        elif self.proxy:
            http_or_socks = self.proxy_socks or "http://"
            return f"{http_or_socks}://{self.proxy}:{self.proxy_port}"
        return None

class DigiProdGenMBAConfig(BaseModel):
    marketplaces: List[DigiProdGenMBAMarketplaceConfig]

    def get_marketplace_config(self, marketplace: MBAMarketplaceDomain) -> DigiProdGenMBAMarketplaceConfig:
        matches = [marketplace_config for marketplace_config in self.marketplaces if marketplace_config.marketplace == marketplace]
        if not matches:
            raise ValueError(f"Configuration for marketplace {marketplace} was not defined")
        return matches[0]

class DigiProdGenViewConfig(BaseModel):
    cards_per_row: int = Field(description="Number of cards (with product info) in one row")

class DigiProdGenImageGenBrConfig(BaseModel):
    outer_pixel_range: int = Field(description="Number of pixel to consider for background removal pixel detection")
    tolerance: int = Field(description="Allowed color difference between a pixel and the average color of the outer pixels. Lower == more strict/less pixels get removed")

class DigiProdGenImageGenConfig(BaseModel):
    background_removal: DigiProdGenImageGenBrConfig

class BackendConfig(BaseModel):
    host: str = Field(default="localhost", description="Address where backend is deployed or localhost.")
    port: int | None
    debug: bool = Field(default=False, description="If true, backend api code is executed via TestClient.")


class DigiProdGenConfig(BaseModel):
    backend: BackendConfig
    mba: DigiProdGenMBAConfig
    browser: DigiProdGenBrowserConfig
    view: DigiProdGenViewConfig
    image_gen: DigiProdGenImageGenConfig