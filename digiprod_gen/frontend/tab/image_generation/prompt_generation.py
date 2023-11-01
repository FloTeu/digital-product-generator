import time
import streamlit as st

from streamlit.delta_generator import DeltaGenerator
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import OutputParserException

from digiprod_gen.backend.text.text_gen_fns import get_midjourney_prompt_gen, mba_products2llm_prompt_gen_input
from digiprod_gen.backend.models.common import MBAMidjourneyOutputModel
from digiprod_gen.frontend.session import read_session
from digiprod_gen.backend.models.session import SessionState
from llm_prompting_gen.generators import ParsablePromptEngineeringGenerator

def prompt_generation(st_tab_ig: DeltaGenerator):
    session_state: SessionState = read_session("session_state")
    mba_products_selected = session_state.crawling_data.get_selected_mba_products()
    llm = ChatOpenAI(temperature=0.7)
    midjourney_prompt_gen = ParsablePromptEngineeringGenerator.from_json("templates/stable_diffusion_prompt_gen.json", llm, pydantic_cls=MBAMidjourneyOutputModel)

    with st_tab_ig, st.spinner('Prompt generation...'):
        # prompt generation
        ts_start = time.time()
        llm_prompt_gen_input = mba_products2llm_prompt_gen_input(mba_products_selected)
        try:
            llm_output: MBAMidjourneyOutputModel = midjourney_prompt_gen.generate(text=llm_prompt_gen_input)
        except OutputParserException:
            # Retry if output has the wrong format
            llm_output: MBAMidjourneyOutputModel = midjourney_prompt_gen.generate(text=llm_prompt_gen_input)

        predicted_prompts = llm_output.image_prompts
        print("mid_gen time elapsed %.2f seconds" % (time.time() - ts_start))
        session_state.image_gen_data.image_gen_prompts = predicted_prompts
        # ts_start = time.time()
        # predicted_prompts = open_ai.mba_products2midjourney_prompts(mba_products_selected)
        # print("openai time elapsed %.2f seconds" % (time.time() - ts_start))
        # write_session([request.get_hash_str(), "predicted_prompts"], predicted_prompts)

    session_state.status.prompts_generated = True


