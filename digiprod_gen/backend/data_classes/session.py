import streamlit as st

from PIL.Image import Image
from digiprod_gen.backend.browser.selenium_fns import SeleniumBrowser
from digiprod_gen.backend.data_classes.mba import MBAProduct, MBAProductCategory, MBAMarketplaceDomain, MBAProductColor, MBAProductFitType


from dataclasses import dataclass, field
from typing import List, Optional
from operator import itemgetter

from digiprod_gen.backend.data_classes.mba import CrawlingMBARequest
from digiprod_gen.backend.data_classes.config import DigiProdGenConfig


@dataclass
class CrawlingData:
    mba_products: List[MBAProduct] = field(default_factory=list)  # crawled mba products
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


@dataclass
class MBAUploadSettings:
    use_defaults: bool = field(default=False)
    product_categories: List[MBAProductCategory] = field(default_factory=list)
    marketplaces: List[MBAMarketplaceDomain] = field(default_factory=list)
    colors: List[MBAProductColor] = field(default_factory=list)
    fit_types: List[MBAProductFitType] = field(default_factory=list)



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
    mba_login_successfull: bool = False
    product_uploaded: bool = False

    def refresh(self):
        """
        Refreshes all status, after the data source has changed
        mba auth status can stay, since its independent of the input data
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

    def get_or_create_sidebar(self):
        if not self.sidebar:
            self.sidebar = st.empty()
        return self.sidebar

@dataclass
class SessionState:
    crawling_request: CrawlingMBARequest | None
    browser: SeleniumBrowser | None
    crawling_data: CrawlingData
    image_gen_data: ImageGenData
    upload_data: MBAUploadData
    status: DigiProdGenStatus
    config: DigiProdGenConfig
    views: DigitProdGenViews
    session_id: str