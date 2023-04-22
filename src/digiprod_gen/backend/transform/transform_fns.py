from digiprod_gen.backend.crawling import parser
from digiprod_gen.backend.crawling.mba.utils import is_product_feature_listing
from digiprod_gen.backend.data_classes import MBAMarketplaceDomain, MBAProduct


from bs4.element import Tag


def overview_product_tag2mba_product(product_tag: Tag, marketplace: MBAMarketplaceDomain) -> MBAProduct:
    product_url = f"https://www.amazon.{marketplace}{parser.overview_product_get_product_url(product_tag)}"
    try:
        price = parser.overview_product_get_price(product_tag)
    except:
        price = None
    return MBAProduct(
        asin = parser.overview_product_get_asin(product_tag),
        title = parser.overview_product_get_title(product_tag),
        image_url = parser.overview_product_get_image_url(product_tag),
        product_url = product_url,
        price=price,
        bullets=None,
        description=None
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
    return mba_product