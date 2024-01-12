from typing import List
from langchain_core.tools import tool
from digiprod_gen.backend.agent.memory import global_memory_container
from digiprod_gen.backend.agent.models.memory import MemoryId, MemoryAddResponse
from digiprod_gen.backend.agent.models.io import MBAProductUploadExport
from digiprod_gen.backend.etl.load_fns import export_upload_mba_product
from digiprod_gen.backend.models.export import MBAExportUploadData, MBAExportUploadProductData
from digiprod_gen.backend.models.mba import MBAUploadSettings, MBAProductCategory, MBAProductFitType, MBAProductColor, MBAMarketplaceDomain
from digiprod_gen.backend.models.session import ProcessingData


@tool("exportUploadMbaProduct", args_schema=MBAProductUploadExport)
def export_upload_data(
        search_term: str,
        title: str,
        brand: str,
        bullets: List[str],
    ):
    """use to export the final generated mba product"""
    if MemoryId.SELECTED_MBA_PRODUCTS not in global_memory_container:
        return {"response": "Failure. No mba products selected yet"}
    if MemoryId.IMAGE_RAW not in global_memory_container:
        return {"response": "Failure. No image generated yet"}

    selected_mba_products = global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS]
    selected_asins = [prod.asin for prod in selected_mba_products]
    # TODO: Change to image upload ready
    img_pil = global_memory_container[MemoryId.IMAGE_RAW]

    product_categories: List[MBAProductCategory] = [MBAProductCategory.SHIRT]
    marketplaces: List[MBAMarketplaceDomain] = [MBAMarketplaceDomain.COM,
                                                MBAMarketplaceDomain.UK,
                                                MBAMarketplaceDomain.JP,
                                                MBAMarketplaceDomain.DE,
                                                MBAMarketplaceDomain.FR,
                                                MBAMarketplaceDomain.IT,
                                                MBAMarketplaceDomain.ES]
    colors: List[MBAProductColor] = [MBAProductColor.BLACK.value, MBAProductColor.ASPHALT_GREY.value, MBAProductColor.NAVY_BLUE.value,
                      MBAProductColor.WHITE.value, MBAProductColor.BROWN.value, MBAProductColor.DARK_HEATHER_GREY.value,
                      MBAProductColor.HEATHER_BLUE.value, MBAProductColor.SILVER_GREY.value, MBAProductColor.SLATE_GREY]
    fit_types: List[MBAProductFitType] = [MBAProductFitType.WOMAN, MBAProductFitType.MEN]

    description = f"""{title} by '{brand}. {bullets[0]}. {bullets[1]}'"""
    export_data = MBAExportUploadData(
        processing_data=ProcessingData(search_term=search_term,
                                       selected_asins=selected_asins,
                                       title_suggestions=global_memory_container[MemoryId.TITLE_SUGGESTIONS],
                                       brand_suggestions=global_memory_container[MemoryId.BRAND_SUGGESTIONS],
                                       bullet_suggestions=global_memory_container[MemoryId.BULLET_SUGGESTIONS],
                                       prompt_suggestions=global_memory_container[MemoryId.PROMPT_SUGGESTIONS],
                                       prompt=""
                                       ),
        product_data=MBAExportUploadProductData(title=title,
                                                brand=brand,
                                                bullets=bullets,
                                                description=description),
        mba_upload_settings=MBAUploadSettings(
            use_defaults=False,
            product_categories=product_categories,
            marketplaces=marketplaces,
            colors=colors,
            fit_types=fit_types
        )
    )
    export_upload_mba_product(img_pil=img_pil, export_data=export_data)
    return {"response": "Successfully exported upload mba products"}
