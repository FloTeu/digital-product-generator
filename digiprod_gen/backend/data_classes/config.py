from pathlib import Path
from typing import List

from pydantic import BaseModel, validator, Field
from digiprod_gen.backend.data_classes.mba import MBAMarketplaceDomain

class DigiProdGenBrowserConfig(BaseModel):
    selenium_data_dir_path: Path

    @validator("selenium_data_dir_path", allow_reuse=True)
    def validate_selenium_data_dir_path(cls, data_dir_path):
        # create dir if not exists
        data_dir_path.mkdir(parents=True, exist_ok=True)
        return data_dir_path

class DigiProdGenMBAMarketplaceConfig(BaseModel):
    marketplace: str
    postcode: str

class DigiProdGenMBAConfig(BaseModel):
    marketplaces: List[DigiProdGenMBAMarketplaceConfig]

    def get_marketplace_config(self, marketplace: MBAMarketplaceDomain) -> DigiProdGenMBAMarketplaceConfig:
        matches = [marketplace_config for marketplace_config in self.marketplaces if marketplace_config.marketplace == marketplace]
        if not matches:
            raise ValueError(f"Configuration for marketplace {marketplace} was not defined")
        return matches[0]

class DigiProdGenViewConfig(BaseModel):
    cards_per_row: int = Field(description="Number of cards (with product info) in one row")

class DigiProdGenConfig(BaseModel):
    mba: DigiProdGenMBAConfig
    browser: DigiProdGenBrowserConfig
    view: DigiProdGenViewConfig