import time
from typing import List
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from digiprod_gen.backend.data_classes.mba import MBAProduct
from digiprod_gen.backend.prompt_engineering import open_ai
from digiprod_gen.backend.prompt_engineering.utils import extract_list_from_output
#from digiprod_gen.backend.prompt_engineering.langchain_fns import get_chat_gpt_model, get_midjourney_prompt_generator_chain
from digiprod_gen.frontend.session import read_session

from digiprod_gen.frontend.tab.crawling.tab_crawling import crawl_mba_overview_and_display
from digiprod_gen.backend.text_generation.data_classes import ProductTextGenerator, MBAMidjourneyPromptGenerator
from digiprod_gen.backend.data_classes.mba import CrawlingMBARequest, MBAProductTextType
from digiprod_gen.backend.data_classes.session import SessionState
from digiprod_gen.backend.text_generation.mba_banned_word import MBA_BANNED_WORDS
from mid_prompt_gen.backend.prompt_gen import MidjourneyPromptGenerator
from mid_prompt_gen.backend.langchain_fns import get_chat_gpt_model
from mid_prompt_gen.backend.midjourney.utils import get_shirt_design_prompt_examples

def combine_bullets(products: List[MBAProduct]) -> str:
    combined_bullets = ""
    for product in products:
        if product.bullets:
            combined_bullets += ' '.join(product.bullets) + ' '
    return combined_bullets.strip()

def get_midjourney_prompt_gen(llm) -> MBAMidjourneyPromptGenerator:
    midjourney_prompt_gen = MBAMidjourneyPromptGenerator(llm)
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

def remove_banned_words(text_suggestions: List[str], banned_words):
    result = []
    for text_suggestion in text_suggestions:
        # Split the string into words
        words = text_suggestion.split()
        # Remove banned words
        words = [word for word in words if word not in banned_words]
        # Join the words back into a string
        modified_string = ' '.join(words)
        result.append(modified_string)
    return result


def prompt_generation_refresh_overview(st_tab_ig: DeltaGenerator, st_tab_crawling: DeltaGenerator):
    session_state: SessionState = read_session("session_state")
    request: CrawlingMBARequest = session_state.crawling_request
    mba_products_selected = session_state.crawling_data.get_selected_mba_products(read_session("selected_designs"))
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
        ts_start = time.time()
        llm_output = midjourney_prompt_gen.generate(text=combine_bullets(mba_products_selected))
        predicted_prompts = extract_list_from_output(llm_output)
        print("mid_gen time elapsed %.2f seconds" % (time.time() - ts_start))
        session_state.image_gen_data.image_gen_prompts = predicted_prompts
        # ts_start = time.time()
        # predicted_prompts = open_ai.mba_products2midjourney_prompts(mba_products_selected)
        # print("openai time elapsed %.2f seconds" % (time.time() - ts_start))
        # write_session([request.get_hash_str(), "predicted_prompts"], predicted_prompts)


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

        session_state.status.prompts_generated = True


