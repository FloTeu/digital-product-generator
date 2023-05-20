from typing import List
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from digiprod_gen.backend.data_classes import CrawlingMBARequest, MBAProduct
from digiprod_gen.backend.prompt_engineering import open_ai
from digiprod_gen.backend.prompt_engineering.utils import extract_list_from_output
#from digiprod_gen.backend.prompt_engineering.langchain_fns import get_chat_gpt_model, get_midjourney_prompt_generator_chain
from digiprod_gen.frontend.session import read_session, write_session

from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display
from digiprod_gen.frontend.tab.image_generation.selected_products import get_selected_mba_products_by_url
from digiprod_gen.backend.text_generation.data_classes import ProductTextGenerator
from digiprod_gen.backend.data_classes import MBAProductTextType
from mid_prompt_gen.backend.prompt_gen import MidjourneyPromptGenerator
from mid_prompt_gen.backend.langchain_fns import get_chat_gpt_model
from mid_prompt_gen.backend.midjourney.utils import get_shirt_design_prompt_examples

def combine_bullets(products: List[MBAProduct]) -> str:
    combined_bullets = ""
    for product in products:
        if product.bullets:
            combined_bullets += ' '.join(product.bullets) + ' '
    return combined_bullets.strip()

def get_midjourney_prompt_gen(llm) -> MidjourneyPromptGenerator:
    midjourney_prompt_gen = MidjourneyPromptGenerator(llm)
    midjourney_prompt_gen.set_context()
    prompt_examples = get_shirt_design_prompt_examples()
    midjourney_prompt_gen.set_few_shot_examples(prompt_examples)
    return midjourney_prompt_gen

def get_product_text_gen(llm, mba_products, mba_product_text_type: MBAProductTextType, marketplace) -> ProductTextGenerator:
    product_text_gen = ProductTextGenerator(llm)
    product_text_gen.set_context()
    few_shot_examples = []
    if mba_product_text_type == MBAProductTextType.BULLET:
        for mba_product in mba_products:
            for bullet in mba_product.bullets:
                few_shot_examples.append(bullet)
    elif mba_product_text_type == MBAProductTextType.BRAND:
        for mba_product in mba_products:
            few_shot_examples.append(mba_product.brand)
    elif mba_product_text_type == MBAProductTextType.TITLE:
        for mba_product in mba_products:
            few_shot_examples.append(mba_product.title)
    product_text_gen.set_few_shot_examples(few_shot_examples, mba_product_text_type)
    product_text_gen._set_human_message(mba_product_text_type, marketplace)
    return product_text_gen

def prompt_generation_refresh_overview(st_tab_ig: DeltaGenerator, st_tab_crawling: DeltaGenerator):
    request: CrawlingMBARequest = read_session("request")
    mba_products_selected = get_selected_mba_products_by_url(request)
    # Make sure user sees overview page and recreate it from session
    crawl_mba_overview_and_display(st_tab_crawling)
    llm = get_chat_gpt_model(temperature=0.7)
    midjourney_prompt_gen = get_midjourney_prompt_gen(llm)
    product_text_gen_brand = get_product_text_gen(llm, mba_products_selected, MBAProductTextType.BRAND, request.marketplace)
    product_text_gen_title = get_product_text_gen(llm, mba_products_selected, MBAProductTextType.TITLE, request.marketplace)
    product_text_gen_bullet = get_product_text_gen(llm, mba_products_selected, MBAProductTextType.BULLET, request.marketplace)
    
    with st_tab_ig, st.spinner('Prompt generation...'):
        # prompt generation
        #answer_chain = get_midjourney_prompt_generator_chain(llm, multiple_suggestions=True)
        #predicted_prompts = extract_list_from_output(answer_chain.run(text=combine_bullets(mba_products_selected)))
        predicted_prompt = midjourney_prompt_gen.generate(text=combine_bullets(mba_products_selected))
        write_session([request.get_hash_str(), "predicted_prompt"], predicted_prompt)
        predicted_prompts = open_ai.mba_products2midjourney_prompts(mba_products_selected)
        write_session([request.get_hash_str(), "predicted_prompts"], predicted_prompts)
        # # bullet generation
        # predicted_bullets = open_ai.mba_products2bullets(mba_products_selected, marketplace=request.marketplace)
        # write_session([request.get_hash_str(), "predicted_bullets"], predicted_bullets)
        # # title generation
        # predicted_titles = open_ai.mba_products2titles(mba_products_selected, marketplace=request.marketplace)
        # write_session([request.get_hash_str(), "predicted_titles"], predicted_titles)
        # # brand generation
        # predicted_brand = open_ai.mba_products2brands(mba_products_selected, marketplace=request.marketplace)
        # write_session([request.get_hash_str(), "predicted_brands"], predicted_brand)


