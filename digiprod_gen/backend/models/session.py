import streamlit as st

from PIL.Image import Image
from pydantic import BaseModel

from digiprod_gen.backend.browser.selenium_fns import SeleniumBrowser
from digiprod_gen.backend.models.mba import MBAProduct, MBAUploadSettings
from digiprod_gen.backend.image.crop import get_mba_design_crop
from digiprod_gen.frontend.backend_caller import BackendCaller

from dataclasses import dataclass, field
from typing import List, Dict
from operator import itemgetter

from digiprod_gen.backend.models.request import CrawlingMBARequest
from digiprod_gen.backend.models.config import DigiProdGenConfig, DigiProdGenMBAMarketplaceConfig


@dataclass
class CrawlingData:
    mba_products: List[MBAProduct] = field(default_factory=list)  # crawled utils products
    selected_designs: List[int] = field(default_factory=list) # user selected products for prompt generation
    mba_product_images: Dict[str, Image] = field(default_factory=dict) # key is mba product id/asin, value is the image

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

    def get_mba_product_image(self, id: str) -> Image | None:
        return self.mba_product_images.get(id, None)

    def get_image_design_crop(self, id: str) -> Image:
        image_pil = self.get_mba_product_image(id)
        if not image_pil:
            raise ValueError("Pillow image not yet set")
        return get_mba_design_crop(image_pil)

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
class MBAImportData:
    last_selected_cat_name: str = field(default="")
    last_selected_index: int = field(default=0)
    selected_import_products: Dict[str, int] = field(default_factory=dict)

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
    import_data: MBAImportData = field(default_factory=MBAImportData)


@dataclass
class DigiProdGenStatus:
    overview_page_crawled: bool = False
    detail_pages_crawled: bool = False
    prompts_generated: bool = False
    image_upload_ready: bool = False
    keywords_extracted: bool = False
    listing_generated: bool = False
    mba_login_otp_required: bool = False
    mba_login_successful: bool = False
    product_uploaded: bool = False
    product_imported: bool = False

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
        self.product_imported = False

@dataclass
class DigitProdGenTabs:
    crawling: st.delta_generator.DeltaGenerator
    image_gen: st.delta_generator.DeltaGenerator
    upload: st.delta_generator.DeltaGenerator
    import_prod: st.delta_generator.DeltaGenerator


@dataclass
class DigitProdGenViews:
    tabs: DigitProdGenTabs | None = None
    sidebar: st.delta_generator.DeltaGenerator | None = None
    overview_designs: st.delta_generator.DeltaGenerator | None = None
    ai_agent: st.delta_generator.DeltaGenerator | None = None

    def get_or_create_sidebar(self):
        if not self.sidebar:
            self.sidebar = st.sidebar.empty()
        return self.sidebar

    def get_or_create_overview_designs(self):
        if not self.overview_designs:
            self.overview_designs = st.empty()
        return self.overview_designs

    def get_or_create_ai_agent(self):
        if not self.ai_agent:
            self.ai_agent = st.empty()
        return self.ai_agent

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


class ProcessingData(BaseModel):
    """Data container for optional export"""
    search_term: str
    selected_asins: List[str]
    keywords: List[str] | None = None
    title_suggestions: List[str]
    brand_suggestions: List[str]
    bullet_suggestions: List[str]
    prompt_suggestions: List[str]
    prompt: str
