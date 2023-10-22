from digiprod_gen.backend.browser.crawling.utils.utils_mba import get_mba_overview_urls
from digiprod_gen.backend.models.mba import MBAProductCategory, CrawlingMBARequest


def mba_product_category2html_row_name(mba_product: MBAProductCategory):
    translate_dict = {
        MBAProductCategory.SHIRT: "Standard t-shirt",
        MBAProductCategory.PREMIUM_SHIRT: "Premium t-shirt",
        MBAProductCategory.V_SHIRT: "V-neck t-shirt",
        MBAProductCategory.TANK_TOP: "Tank top",
        MBAProductCategory.LONG_SLEEVE: "Long sleeve t-shirt",
        MBAProductCategory.RAGLAN: "Raglan",
        MBAProductCategory.SWEATSHIRT: "Sweatshirt",
        MBAProductCategory.HOODIE: "Pullover hoodie",
        MBAProductCategory.ZIP_HOODIE: "Zip hoodie",
        MBAProductCategory.POP_SOCKET: "PopSockets grip",
        MBAProductCategory.IPHONE_CASE: "iPhone cases",
        MBAProductCategory.SAMSUNG_GALAXY_CASE: "Samsung Galaxy cases",
        MBAProductCategory.TOTE_BAG: "Tote bag",
        MBAProductCategory.THROW_PILLOWS: "Throw pillows"
    }
    return translate_dict.get(mba_product, None)


def request2mba_overview_url(request: CrawlingMBARequest) -> str:
    start_page = 0
    number_pages = 1
    mba_urls = get_mba_overview_urls(
        marketplace=request.marketplace,
        search_term=request.search_term,
        product_category=request.product_category,
        start_page=start_page,
        number_pages=number_pages
    )
    return mba_urls[0]
