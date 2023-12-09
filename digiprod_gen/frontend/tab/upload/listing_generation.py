import time
import streamlit as st

from typing import List
from streamlit.delta_generator import DeltaGenerator

from digiprod_gen.backend.text.text_gen_fns import remove_banned_words
from digiprod_gen.backend.models.mba import MBAProductTextType
from digiprod_gen.backend.models.request import KeywordExtractionRequest, ListingGenRequest
from digiprod_gen.backend.models.session import SessionState
from digiprod_gen.frontend.session import read_session


def listing_generation(st_tab_ig: DeltaGenerator):
    session_state: SessionState = read_session("session_state")
    backend_caller = session_state.backend_caller
    mba_products_selected = session_state.crawling_data.get_selected_mba_products()

    with st_tab_ig, st.spinner('Listing generation...'):
        keyword_text = ""
        for mba_product in mba_products_selected:
            keyword_text += f"{mba_product.brand} {mba_product.title} {' '.join([bullet for bullet in mba_product.bullets])}\n"
        keywords: List[str] = backend_caller.post(f"/text/extract/keywords?temperature=0.7", data=KeywordExtractionRequest(text=keyword_text).model_dump_json()).json()
        keywords_str = ",".join(keywords)
        ts_start = time.time()
        # bullet generation
        examples = [remove_banned_words(bullet) for mba_product in mba_products_selected for bullet in mba_product.bullets]
        session_state.upload_data.predicted_bullets = backend_caller.post(f"/text/gen/listings?temperature=0.7", data=ListingGenRequest(examples=examples, keywords=keywords_str, type=MBAProductTextType.BULLET).model_dump_json()).json()
        # title generation
        examples = [remove_banned_words(mba_product.title) for mba_product in mba_products_selected]
        session_state.upload_data.predicted_titles = backend_caller.post(f"/text/gen/listings?temperature=0.7", data=ListingGenRequest(examples=examples, keywords=keywords_str, type=MBAProductTextType.TITLE).model_dump_json()).json()
        # brand generation
        examples = [remove_banned_words(mba_product.brand) for mba_product in mba_products_selected]
        session_state.upload_data.predicted_brands = backend_caller.post(f"/text/gen/listings?temperature=0.7", data=ListingGenRequest(examples=examples, keywords=keywords_str, type=MBAProductTextType.BRAND).model_dump_json()).json()
        print("product texts elapsed %.2f seconds" % (time.time() - ts_start))

    session_state.status.listing_generated = True


