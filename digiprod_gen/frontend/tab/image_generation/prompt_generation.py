import time
import streamlit as st

from streamlit.delta_generator import DeltaGenerator
from langchain.chat_models import ChatOpenAI

from digiprod_gen.backend.generative_ai.text.text_gen_fns import get_midjourney_prompt_gen, mba_products2llm_prompt_gen_input
from digiprod_gen.backend.prompt_engineering.utils import extract_list_from_output
from digiprod_gen.backend.data_classes.common import MBAMidjourneyOutputModel
from digiprod_gen.frontend.session import read_session
from digiprod_gen.backend.data_classes.session import SessionState


def prompt_generation(st_tab_ig: DeltaGenerator):
    session_state: SessionState = read_session("session_state")
    mba_products_selected = session_state.crawling_data.get_selected_mba_products()
    llm = ChatOpenAI(temperature=0.7)
    midjourney_prompt_gen = get_midjourney_prompt_gen(llm)

    with st_tab_ig, st.spinner('Prompt generation...'):
        # prompt generation
        ts_start = time.time()
        llm_prompt_gen_input = mba_products2llm_prompt_gen_input(mba_products_selected)
        llm_output: MBAMidjourneyOutputModel = midjourney_prompt_gen.generate(text=llm_prompt_gen_input)
        predicted_prompts = llm_output.image_prompts
        print("mid_gen time elapsed %.2f seconds" % (time.time() - ts_start))
        session_state.image_gen_data.image_gen_prompts = predicted_prompts
        # ts_start = time.time()
        # predicted_prompts = open_ai.mba_products2midjourney_prompts(mba_products_selected)
        # print("openai time elapsed %.2f seconds" % (time.time() - ts_start))
        # write_session([request.get_hash_str(), "predicted_prompts"], predicted_prompts)

    session_state.status.prompts_generated = True


