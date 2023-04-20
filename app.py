import math

import requests
import streamlit as st
from bs4 import BeautifulSoup
from io import BytesIO
from bs4.element import Tag
from typing import List
from operator import itemgetter
from collections import deque


from digiprod_gen.backend.data_classes import MBAMarketplaceDomain, CrawlingMBARequest, MBAProductCategory, MBAProduct
from digiprod_gen.backend.utils import split_list, marketplace2currency, get_price_display_str, write_session, read_session, request2mba_overview_url
from digiprod_gen.backend.crawling.utils import get_random_headers, is_product_feature_listing
from digiprod_gen.backend.crawling.proxies import get_random_private_proxy
from digiprod_gen.backend.crawling import parser
from digiprod_gen.backend.prompt_engineering import open_ai
from digiprod_gen.backend.image import conversion as img_conversion
from digiprod_gen.backend.image.background_removal import remove_outer_pixels
from digiprod_gen.backend.image.upscale import pil_upscale

#overview_product_get_image_url, overview_product_get_asin, overview_product_get_product_url, overview_product_get_title

MAX_SHIRTS_PER_ROW = 4
DEVICE = "auto"

st.header("MBA Bullet Feature Extractor")
tab_crawling, tab_ig, tab_upload = st.tabs(["Crawling", "Image Generation", "MBA Upload"])

@st.cache_data
def image_url2image_bytes_io(image_url: str) -> BytesIO:
    response = requests.get(image_url)
    return BytesIO(response.content)


def update_mba_request():
    marketplace = st.session_state["marketplace"]
    search_term = st.session_state["search_term"]
    proxy = get_random_private_proxy(st.secrets.proxy_perfect_privacy.user_name, st.secrets.proxy_perfect_privacy.password,marketplace=marketplace)
    request = CrawlingMBARequest(marketplace=marketplace, product_category=MBAProductCategory.SHIRT,
                                 search_term=search_term, headers=get_random_headers(marketplace), proxy=proxy, mba_overview_url=None)
    request.mba_overview_url = request2mba_overview_url(request)
    write_session("request", request)

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

def is_mba_product(product_tag: Tag) -> bool:
    """product is considered as mba product if it contains a asin id"""
    try:
        asin = parser.overview_product_get_asin(product_tag)
        return True
    except:
        return False

def crawl_overview(request: CrawlingMBARequest):
    mba_products: List[MBAProduct] = []
    response = send_mba_overview_request(request)
    if response.status_code != 200:
        # retry with new headers
        update_mba_request()
        request = read_session("request")
        response = send_mba_overview_request(request)
        if response.status_code != 200:
            tab_crawling.write("Crawling was not successfull")

    # Parse to beautiful soup
    soup = BeautifulSoup(response.content, 'html.parser')
    product_tags = soup.find_all("div", {"class": "sg-col-inner"})
    mba_product_tags = [p for p in product_tags if is_mba_product(p)]
    for product_tag in mba_product_tags:
        mba_product: MBAProduct = overview_product_tag2mba_product(product_tag, marketplace=request.marketplace)
        mba_products.append(mba_product)
    # save to session
    write_session([request.get_hash_str(), "mba_products"], mba_products)


def send_mba_overview_request(request):
    print(request.proxy)
    response = requests.get(
        url=request.mba_overview_url,
        headers=request.headers,
        proxies = {
            "http": request.proxy,
            "https": request.proxy
        }
    )
    return response


def crawl_overview_and_display():
    request: CrawlingMBARequest = read_session("request")
    marketplace = request.marketplace
    with tab_crawling:
        display_start_crawling = st.empty()
        display_start_crawling.write("Start crawling...")
        currency_str = marketplace2currency(marketplace)

        mba_products = read_session([request.get_hash_str(), "mba_products"])
        if not mba_products:
            crawl_overview(request)
            mba_products = read_session([request.get_hash_str(), "mba_products"])

        if read_session("is_debug"):
            mba_products = mba_products[0:8]

        #with tab_crawling.expander("Crawling results", expanded=True):
        display_mba_overview_products(currency_str, marketplace, request, mba_products)
        display_start_crawling.empty()

def display_mba_overview_products(currency_str, marketplace, request: CrawlingMBARequest, mba_products: List[MBAProduct]):
    progress_text = "Crawling in progress. Please wait."
    crawling_progress_bar = st.progress(0, text=progress_text)
    display_overview_products = st.empty()
    display_cols = display_overview_products.columns(MAX_SHIRTS_PER_ROW)
    for j, mba_products_splitted_list in enumerate(split_list(mba_products, MAX_SHIRTS_PER_ROW)):
        for i, mba_product in enumerate(mba_products_splitted_list):
            crawling_progress_bar.progress(math.ceil(100 / len(mba_products) * ((j * MAX_SHIRTS_PER_ROW) + i)) + 1,
                                           text=progress_text)
            image_bytes_io: BytesIO = image_url2image_bytes_io(mba_product.image_url)
            # image_pil = Image.open(image_bytes_io)
            display_cols[i].image(image_bytes_io)
            color = "black" if not mba_product.bullets else "green"
            display_cols[i].markdown(f":{color}[{(j * MAX_SHIRTS_PER_ROW) + i + 1}. {mba_product.title}]")
            display_cols[i].write(f"Price: {get_price_display_str(marketplace, mba_product.price, currency_str)}")

    crawling_progress_bar.empty()
    write_session([request.get_hash_str(), "display_overview_products"], display_overview_products)

def get_selected_mba_products_by_url(request: CrawlingMBARequest) -> List[MBAProduct]:
    mba_products = read_session([request.get_hash_str(), "mba_products"])
    return get_selected_mba_products(mba_products)

def get_selected_mba_products(mba_products) -> List[MBAProduct]:
    selected_designs = st.session_state['selected_designs']
    # transform human selection to machine index
    selected_designs_i = [i - 1 for i in selected_designs]
    if not selected_designs:
        return []
    if len(selected_designs_i) == 1:
        return [mba_products[selected_designs_i[0]]]
    else:
        return list(itemgetter(*selected_designs_i)(mba_products))
def crawl_details(request):
    # with tab_crawling:
    mba_products = read_session([request.get_hash_str(), "mba_products"])
    headers = request.headers
    mba_products_selected = get_selected_mba_products(mba_products)

    for i, mba_product in enumerate(mba_products_selected):
        mba_product_detailed = read_session(mba_product.asin)
        if mba_product_detailed != None:
            # Detailed mba product is already available in session
            mba_products_selected[i] = mba_product_detailed
            continue
        # Else crawl detail information
        mba_product_detailed = mba_product
        headers["referer"] = request.mba_overview_url
        response_product_url = requests.get(
            url=mba_product_detailed.product_url,
            headers=headers,
            proxies = {
                "http": request.proxy,
                "https": request.proxy
            }
        )
        soup = BeautifulSoup(response_product_url.content, 'html.parser')
        if "captcha" in soup.prettify():
            raise ValueError("Got a captcha :(")
        # call by reference change of mba_products
        extend_mba_product(mba_product_detailed, soup, request.marketplace)
        # save data to session
        write_session(mba_product.asin, mba_product_detailed)
        mba_products_selected[i] = mba_product_detailed
        #mba_products[selected_designs_i[i]] = mba_product_detailed
    write_session([request.get_hash_str(), "mba_products"], mba_products)
    return mba_products_selected

def crawl_details_update_overview_page():
    request: CrawlingMBARequest = read_session("request")
    # Make sure user sees overview page and recreate it from session
    crawl_overview_and_display()

    with tab_ig, st.spinner('Crawling detail pages...'):
        # crawl new detail pages
        crawl_details(request)
        # refresh overview page
        display_overview_products = read_session([request.get_hash_str(), "display_overview_products"])
        display_overview_products.empty()
    crawl_overview_and_display()
    write_session([request.get_hash_str(), "detail_pages_crawled"], True)


def prompt_generation_refresh_overview():
    request: CrawlingMBARequest = read_session("request")
    mba_products_selected = get_selected_mba_products_by_url(request)
    # Make sure user sees overview page and recreate it from session
    crawl_overview_and_display()
    with tab_ig, st.spinner('Prompt generation...'):
        # prompt generation
        predicted_prompts = open_ai.mba_products2midjourney_prompts(mba_products_selected)
        write_session([request.get_hash_str(), "predicted_prompts"], predicted_prompts)
        # bullet generation
        predicted_bullets = open_ai.mba_products2listings(mba_products_selected, marketplace=request.marketplace)
        write_session([request.get_hash_str(), "predicted_bullets"], predicted_bullets)

def display_mba_products(mba_products_selected: List[MBAProduct]):
    with st.expander("Collapse selected mba products", expanded=True):
        display_cols = st.columns(MAX_SHIRTS_PER_ROW)
        for j, mba_products_splitted_list in enumerate(split_list(mba_products_selected, MAX_SHIRTS_PER_ROW)):
            for i, mba_product in enumerate(mba_products_splitted_list):
                image_bytes_io: BytesIO = image_url2image_bytes_io(mba_product.image_url)
                display_cols[i].image(image_bytes_io)
                display_cols[i].markdown(f":black[{mba_product.title}]")
                for bullet_i, bullet in enumerate(mba_product.bullets):
                    display_cols[i].write(f"Bullets {bullet_i+1}: {bullet}")

def main():
    st.sidebar.subheader("1. Crawling MBA Overview")
    st.sidebar.checkbox(label="Speed up Crawling", value=True, key="is_debug")
    st.sidebar.text_input(value="Pew Pew Madafakas", label="Search Term", on_change=update_mba_request, key="search_term")
    st.sidebar.selectbox("MBA Marketplace",
                                       options=[MBAMarketplaceDomain.COM, MBAMarketplaceDomain.DE], on_change=update_mba_request, key="marketplace")
    request = read_session("request")
    if request == None:
        update_mba_request()
        request = read_session("request")


    st.sidebar.button("Start Crawling", on_click=crawl_overview_and_display)

    mba_products = read_session([request.get_hash_str(), "mba_products"])
    if mba_products != None:
        st.sidebar.subheader("2. Crawling MBA Product Pages")
        st.sidebar.multiselect("Select Designs for prompt generation:", [i+1 for i in range(len(mba_products))], key='selected_designs', on_change=crawl_overview_and_display)
        st.sidebar.button("Start Crawling Details", on_click=crawl_details_update_overview_page, key="button_crawl_detail")

        mba_products_selected = get_selected_mba_products_by_url(request)
        if mba_products_selected and read_session([request.get_hash_str(), "detail_pages_crawled"]):
            st.sidebar.subheader("3. Prompt Generation")
            st.sidebar.button("Start Prompt Generation", on_click=prompt_generation_refresh_overview, key="button_prompt_generation")
            predicted_prompts = read_session([request.get_hash_str(), "predicted_prompts"])
            predicted_bullets = read_session([request.get_hash_str(), "predicted_bullets"])
            with tab_ig:
                st.subheader("Selected MBA Products")
                display_mba_products(mba_products_selected)
            if predicted_prompts:
                with tab_ig:
                    st.subheader("Suggested Prompts")
                    st.write(predicted_prompts)
                st.markdown("Please use one of the example Prompts to generate an image with Midjourney. \nYou can upload the image afterwards an proceed.")
                st.subheader("Upload Image to MBA")
                image = st.file_uploader("Image:", type=["png", "jpg", "jpeg"], key="tab_ig_image")
                if image:
                    image_pil = img_conversion.bytes2pil(image.getvalue())
                    st.image(image_pil)
                    image_pil_br = read_session("image_pil_br")
                    if st.button("Remove Background"):
                        st.write("Removed Background")
                        image_pil_br = remove_outer_pixels(image_pil, buffer=0)
                        write_session("image_pil_br", image_pil_br)
                        st.image(image_pil_br)
                    if st.button("Upscale") and image_pil_br:
                        image_pil_br_upscale = pil_upscale(image_pil_br, (4500, 5400))
                        image_pil_br_upscale.save("test.png")
                        st.image(image_pil_br_upscale)

            if predicted_bullets:
                with tab_upload:
                    st.subheader("Suggested Bullets")
                    st.selectbox("Bullet 1:", predicted_bullets, on_change=crawl_overview_and_display, key="bullet1")
                    predicted_bullets_shifted = deque(predicted_bullets)
                    predicted_bullets_shifted.rotate(-1)
                    st.selectbox("Bullet 2:", predicted_bullets_shifted, on_change=crawl_overview_and_display, key="bullet2")
                    st.text_area("Bullet 1:", value=read_session("bullet1"))
                    st.text_area("Bullet 2:", value=read_session("bullet2"))

        if read_session([request.get_hash_str(), "predicted_bullets"]):
            with tab_upload:
                st.subheader("Upload Image to MBA")
                image = st.file_uploader("Image:", type=["png", "jpg", "jpeg"], key="tab_upload_image")
                image_pil = img_conversion(image.getvalue())
                st.write(image_pil)
                if st.button("Remove Background"):
                    st.write("Removed Background")
                    from rembg import remove
                    image_pil_br = remove(image_pil)
                    st.write(image_pil_br)

        t = 0

if __name__ == "__main__":
    main()
