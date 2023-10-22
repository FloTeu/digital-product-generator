import streamlit as st

from PIL.Image import Image
from digiprod_gen.backend.browser.selenium_fns import SeleniumBrowser
from digiprod_gen.backend.models.mba import MBAProduct, MBAUploadSettings
from digiprod_gen.frontend.backend_caller import BackendCaller

from dataclasses import dataclass, field
from typing import List
from operator import itemgetter

from digiprod_gen.backend.models.request import CrawlingMBARequest
from digiprod_gen.backend.models.config import DigiProdGenConfig, DigiProdGenMBAMarketplaceConfig


@dataclass
class CrawlingData:
    mba_products: List[MBAProduct] = field(default_factory=list)  # crawled utils products
    selected_designs: List[int] = field(default_factory=list) # user selected products for prompt generation

    def get_selected_mba_products(self) -> List[MBAProduct]:
        """
            selected_designs: Human input of selected designs for prompt generation. Starting with 1, 2 and so on.
        """
        if not self.selected_designs:
            return []
        # transform human selection to machine index
        selected_designs_i = [i - 1 for i in self.selected_designs]
        if len(selected_designs_i) == 1:
            return [self.mba_products[selected_designs_i[0]]]
        else:
            return list(itemgetter(*selected_designs_i)(self.mba_products))

@dataclass
class ImageGenData:
    image_gen_prompts: List[str] = field(default_factory=list)
    image_gen_prompt_selected: str | None = None
    image_pil_generated: Image | None = None
    image_pil_outpainted: Image | None = None
    image_pil_upscaled: Image | None = None
    image_pil_background_removed: Image | None = None
    image_pil_upload_ready: Image | None = None

    def reset_image_data(self):
        """Reset all image editings after the base generated one"""
        self.image_pil_outpainted = None
        self.image_pil_upscaled = None
        self.image_pil_background_removed = None
        self.image_pil_upload_ready = None

    def get_valid_upload_png(self):
        return self.image_pil_upload_ready


@dataclass
class MBAUploadData:
    predicted_brands: List[str] = field(default_factory=list)
    predicted_titles: List[str] = field(default_factory=list)
    predicted_bullets: List[str] = field(default_factory=list)
    title: str | None = None
    brand: str | None = None
    bullet_1: str | None = None
    bullet_2: str | None = None
    description: str | None = None
    settings: MBAUploadSettings = field(default_factory=MBAUploadSettings)


@dataclass
class DigiProdGenStatus:
    overview_page_crawled: bool = False
    detail_pages_crawled: bool = False
    prompts_generated: bool = False
    image_upload_ready: bool = False
    listing_generated: bool = False
    mba_login_otp_required: bool = False
    mba_login_successful: bool = False
    product_uploaded: bool = False

    def refresh(self):
        """
        Refreshes all status, after the data source has changed
        utils auth status can stay, since its independent of the input data
        """
        self.overview_page_crawled = False
        self.detail_pages_crawled = False
        self.prompts_generated = False
        self.image_upload_ready = False
        self.listing_generated = False
        self.product_uploaded = False


@dataclass
class DigitProdGenViews:
    sidebar: st.delta_generator.DeltaGenerator | None = None
    overview_designs: st.delta_generator.DeltaGenerator | None = None
    def get_or_create_sidebar(self):
        if not self.sidebar:
            self.sidebar = st.sidebar.empty()
        return self.sidebar

    def get_or_create_overview_designs(self):
        if not self.overview_designs:
            self.overview_designs = st.empty()
        return self.overview_designs

@dataclass
class SessionState:
    crawling_request: CrawlingMBARequest | None
    browser: SeleniumBrowser | None
    crawling_data: CrawlingData
    image_gen_data: ImageGenData
    upload_data: MBAUploadData
    status: DigiProdGenStatus
    config: DigiProdGenConfig
    backend_caller: BackendCaller
    views: DigitProdGenViews
    session_id: str

    def get_marketplace_config(self, marketplace: str | None = None) -> DigiProdGenMBAMarketplaceConfig:
        marketplace = marketplace or self.crawling_request.marketplace
        return self.config.mba.get_marketplace_config(marketplace)