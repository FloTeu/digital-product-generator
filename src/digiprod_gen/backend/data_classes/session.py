from PIL.Image import Image
from digiprod_gen.backend.browser.selenium_fns import SeleniumBrowser
from digiprod_gen.backend.data_classes.mba import MBAProduct


from dataclasses import dataclass, field
from typing import List, Optional
from operator import itemgetter

from digiprod_gen.backend.data_classes.mba import CrawlingMBARequest


@dataclass
class CrawlingData:
    mba_products: List[MBAProduct] = field(default_factory=list)  # crawled mba products

    def get_selected_mba_products(self, selected_designs: List[int]) -> List[MBAProduct]:
        """
            selected_designs: Human input of selected designs for prompt generation. Starting with 1, 2 and so on.
        """
        # transform human selection to machine index
        selected_designs_i = [i - 1 for i in selected_designs]
        if not selected_designs:
            return []
        if len(selected_designs_i) == 1:
            return [self.mba_products[selected_designs_i[0]]]
        else:
            return list(itemgetter(*selected_designs_i)(self.mba_products))


@dataclass
class ImageGenData:
    image_gen_prompts: List[str] = field(default_factory=list)
    image_pil_background_removed: Image | None = None 
    image_pil_upload_ready: Image | None = None 


@dataclass
class MBAUploadData:
    predicted_brands: List[str] = field(default_factory=list)
    predicted_titles: List[str] = field(default_factory=list)
    predicted_bullets: List[str] = field(default_factory=list)


@dataclass
class DigiProdGenStatus:
    overview_page_crawled: bool = False
    detail_pages_crawled: bool = False
    prompts_generated: bool = False
    image_upload_ready: bool = False
    mba_login_successfull: bool = False
    product_uploaded: bool = False


@dataclass
class SessionState:
    crawling_request: CrawlingMBARequest
    browser: SeleniumBrowser
    crawling_data: CrawlingData
    image_gen_data: ImageGenData
    upload_data: MBAUploadData
    status: DigiProdGenStatus
    session_id: str