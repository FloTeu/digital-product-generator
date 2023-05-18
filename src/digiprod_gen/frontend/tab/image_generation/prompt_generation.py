from typing import List
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from digiprod_gen.backend.data_classes import CrawlingMBARequest, MBAProduct
from digiprod_gen.backend.prompt_engineering import open_ai
from digiprod_gen.backend.prompt_engineering.utils import extract_list_from_output
from digiprod_gen.backend.prompt_engineering.langchain_fns import get_chat_gpt_model, get_midjourney_prompt_generator_chain
from digiprod_gen.frontend.session import read_session, write_session

from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display
from digiprod_gen.frontend.tab.image_generation.selected_products import get_selected_mba_products_by_url

def combine_bullets(products: List[MBAProduct]) -> str:
    combined_bullets = ""
    for product in products:
        if product.bullets:
            combined_bullets += ' '.join(product.bullets) + ' '
    return combined_bullets.strip()

def prompt_generation_refresh_overview(st_tab_ig: DeltaGenerator, st_tab_crawling: DeltaGenerator):
    request: CrawlingMBARequest = read_session("request")
    mba_products_selected = get_selected_mba_products_by_url(request)
    # Make sure user sees overview page and recreate it from session
    crawl_mba_overview_and_display(st_tab_crawling)
    llm = get_chat_gpt_model(temperature=0.7)
    
    with st_tab_ig, st.spinner('Prompt generation...'):
        # prompt generation
        answer_chain = get_midjourney_prompt_generator_chain(llm, multiple_suggestions=True)
        predicted_prompts = extract_list_from_output(answer_chain.run(text=combine_bullets(mba_products_selected)))
        write_session([request.get_hash_str(), "predicted_prompt"], predicted_prompts)
        predicted_prompts = open_ai.mba_products2midjourney_prompts(mba_products_selected)
        write_session([request.get_hash_str(), "predicted_prompts"], predicted_prompts)
        # bullet generation
        predicted_bullets = open_ai.mba_products2bullets(mba_products_selected, marketplace=request.marketplace)
        write_session([request.get_hash_str(), "predicted_bullets"], predicted_bullets)
        # title generation
        predicted_titles = open_ai.mba_products2titles(mba_products_selected, marketplace=request.marketplace)
        write_session([request.get_hash_str(), "predicted_titles"], predicted_titles)
        # brand generation
        predicted_brand = open_ai.mba_products2brands(mba_products_selected, marketplace=request.marketplace)
        write_session([request.get_hash_str(), "predicted_brands"], predicted_brand)


