import time
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from digiprod_gen.backend.generative_ai.text.text_gen_fns import combine_bullets, get_midjourney_prompt_gen, add_aspect_ration
from digiprod_gen.backend.prompt_engineering.utils import extract_list_from_output
#from digiprod_gen.backend.prompt_engineering.langchain_fns import get_chat_gpt_model, get_midjourney_prompt_generator_chain
from digiprod_gen.frontend.session import read_session
from digiprod_gen.backend.data_classes.session import SessionState
from mid_prompt_gen.backend.langchain_fns import get_chat_gpt_model


def prompt_generation(st_tab_ig: DeltaGenerator):
    session_state: SessionState = read_session("session_state")
    mba_products_selected = session_state.crawling_data.get_selected_mba_products(read_session("selected_designs"))
    llm = get_chat_gpt_model(temperature=0.7)
    midjourney_prompt_gen = get_midjourney_prompt_gen(llm)

    with st_tab_ig, st.spinner('Prompt generation...'):
        # prompt generation
        ts_start = time.time()
        llm_output = midjourney_prompt_gen.generate(text=combine_bullets(mba_products_selected))
        predicted_prompts = add_aspect_ration(extract_list_from_output(llm_output))
        print("mid_gen time elapsed %.2f seconds" % (time.time() - ts_start))
        session_state.image_gen_data.image_gen_prompts = predicted_prompts
        # ts_start = time.time()
        # predicted_prompts = open_ai.mba_products2midjourney_prompts(mba_products_selected)
        # print("openai time elapsed %.2f seconds" % (time.time() - ts_start))
        # write_session([request.get_hash_str(), "predicted_prompts"], predicted_prompts)

    session_state.status.prompts_generated = True


