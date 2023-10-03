from digiprod_gen.backend.browser.crawling import parser
from digiprod_gen.backend.browser.crawling.mba.utils import is_product_feature_listing
from digiprod_gen.backend_api.models.mba import MBAProduct


from bs4.element import Tag

from digiprod_gen.backend_api.models.mba import MBAMarketplaceDomain, MBAProductCategory


def overview_product_tag2mba_product(product_tag: Tag, marketplace: MBAMarketplaceDomain) -> MBAProduct:
    product_url = f"https://www.amazon.{marketplace}{parser.overview_product_get_product_url(product_tag)}"
    try:
        price = parser.overview_product_get_price(product_tag)
    except:
        price = None
    # TODO: Try to get brand in detail page crawling
    try:
        brand = parser.overview_product_get_brand(product_tag)
    except:
        brand = None
    return MBAProduct(
        asin = parser.overview_product_get_asin(product_tag),
        title = parser.overview_product_get_title(product_tag),
        image_url = parser.overview_product_get_image_url(product_tag),
        product_url = product_url,
        brand=brand,
        price=price,
        #bullets=[],
        description=None,
        image_pil=None,
        image_prompt=None,
        image_text_caption=None,
      )


def extend_mba_product(mba_product: MBAProduct, product_tag: Tag, marketplace: MBAMarketplaceDomain) -> MBAProduct:
    bullets = parser.get_bullets(product_tag)
    mba_product.bullets = [b for b in bullets if is_product_feature_listing(marketplace, b)]
    try:
        mba_product.description = parser.get_description(product_tag)
    except:
        pass
    try:
        mba_product.price = parser.get_price(product_tag)
    except:
        pass
    if not mba_product.brand:
        try:
            mba_product.brand = parser.get_brand(product_tag)
        except:
            pass

    return mba_product

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