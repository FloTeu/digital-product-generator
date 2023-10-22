import time
import streamlit as st

from streamlit.delta_generator import DeltaGenerator
from langchain.chat_models import ChatOpenAI

from digiprod_gen.backend_api.text.text_gen_fns import get_product_text_gen, remove_banned_words
from digiprod_gen.backend.prompt_engineering.utils import extract_list_from_output
from digiprod_gen.frontend.session import read_session

from digiprod_gen.backend_api.models.mba import CrawlingMBARequest, MBAProductTextType, MBAMarketplaceDomain
from digiprod_gen.backend_api.models.session import SessionState
from digiprod_gen.backend_api.text.mba_banned_word import MBA_BANNED_WORDS


def listing_generation(st_tab_ig: DeltaGenerator):
    session_state: SessionState = read_session("session_state")
    request: CrawlingMBARequest = session_state.crawling_request
    mba_products_selected = session_state.crawling_data.get_selected_mba_products()
    llm = ChatOpenAI(temperature=0.7)
    # Create english output and let amazon translate it afterwards
    product_text_gen_brand = get_product_text_gen(llm, mba_products_selected, MBAProductTextType.BRAND, MBAMarketplaceDomain.COM)
    product_text_gen_title = get_product_text_gen(llm, mba_products_selected, MBAProductTextType.TITLE, MBAMarketplaceDomain.COM)
    product_text_gen_bullet = get_product_text_gen(llm, mba_products_selected, MBAProductTextType.BULLET, MBAMarketplaceDomain.COM)

    with st_tab_ig, st.spinner('Listing generation...'):
        ts_start = time.time()
        # bullet generation
        predicted_bullets = extract_list_from_output(product_text_gen_bullet.generate(mba_text_type=MBAProductTextType.BULLET))
        session_state.upload_data.predicted_bullets = remove_banned_words(predicted_bullets, MBA_BANNED_WORDS)
        # title generation
        predicted_titles = extract_list_from_output(product_text_gen_title.generate(mba_text_type=MBAProductTextType.TITLE))
        session_state.upload_data.predicted_titles = remove_banned_words(predicted_titles, MBA_BANNED_WORDS)
        # brand generation
        predicted_brands = extract_list_from_output(product_text_gen_brand.generate(mba_text_type=MBAProductTextType.BRAND))
        session_state.upload_data.predicted_brands = remove_banned_words(predicted_brands, MBA_BANNED_WORDS)
        print("product texts elapsed %.2f seconds" % (time.time() - ts_start))

    session_state.status.listing_generated = True


