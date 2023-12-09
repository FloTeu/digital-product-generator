import time
import streamlit as st

from typing import List
from streamlit.delta_generator import DeltaGenerator
from langchain.chat_models import ChatOpenAI

from digiprod_gen.backend.text.text_gen_fns import get_product_text_gen, remove_banned_words_from_list
from digiprod_gen.backend.models.mba import MBAProductTextType
from digiprod_gen.backend.models.request import KeywordExtractionRequest, ListingGenRequest
from digiprod_gen.backend.models.session import SessionState
from digiprod_gen.backend.prompt_engineering.utils import extract_list_from_output
from digiprod_gen.backend.text.mba_banned_word import MBA_BANNED_WORDS
from digiprod_gen.frontend.session import read_session


def listing_generation(st_tab_ig: DeltaGenerator):
    session_state: SessionState = read_session("session_state")
    backend_caller = session_state.backend_caller
    mba_products_selected = session_state.crawling_data.get_selected_mba_products()
    llm = ChatOpenAI(temperature=0.7)
    # Create english output and let amazon translate it afterwards
    product_text_gen_brand = get_product_text_gen(llm, mba_products_selected, MBAProductTextType.BRAND)
    product_text_gen_bullet = get_product_text_gen(llm, mba_products_selected, MBAProductTextType.BULLET)

    with st_tab_ig, st.spinner('Listing generation...'):
        keyword_text = ""
        for mba_product in mba_products_selected:
            keyword_text += f"{mba_product.brand} {mba_product.title} {' '.join([bullet for bullet in mba_product.bullets])}\n"
        keywords: List[str] = backend_caller.post(f"/text/extract/keywords?temperature=0.7", data=KeywordExtractionRequest(text=keyword_text).model_dump_json()).json()
        keywords_str = ",".join(keywords)
        ts_start = time.time()
        # bullet generation
        session_state.upload_data.predicted_bullets = backend_caller.post(f"/text/gen/listings?temperature=0.7", data=ListingGenRequest(mba_products=mba_products_selected, keywords=keywords_str, type=MBAProductTextType.BULLET).model_dump_json()).json()
        # title generation
        session_state.upload_data.predicted_titles = backend_caller.post(f"/text/gen/listings?temperature=0.7", data=ListingGenRequest(mba_products=mba_products_selected, keywords=keywords_str, type=MBAProductTextType.TITLE).model_dump_json()).json()
        # brand generation
        session_state.upload_data.predicted_brands = backend_caller.post(f"/text/gen/listings?temperature=0.7", data=ListingGenRequest(mba_products=mba_products_selected, keywords=keywords_str, type=MBAProductTextType.BRAND).model_dump_json()).json()
        print("product texts elapsed %.2f seconds" % (time.time() - ts_start))

    session_state.status.listing_generated = True


