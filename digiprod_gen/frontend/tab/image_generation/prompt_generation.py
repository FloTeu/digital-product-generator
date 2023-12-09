import time
import json
import streamlit as st

from streamlit.delta_generator import DeltaGenerator
from digiprod_gen.backend.models.session import SessionState
from digiprod_gen.frontend.session import read_session

def prompt_generation(st_tab_ig: DeltaGenerator):
    session_state: SessionState = read_session("session_state")
    mba_products_selected = session_state.crawling_data.get_selected_mba_products()
    with st_tab_ig, st.spinner('Prompt generation...'):
        # prompt generation
        ts_start = time.time()
        json_data = json.dumps([item.dict() for item in mba_products_selected])
        session_state.image_gen_data.image_gen_prompts = session_state.backend_caller.post(f"/text/prompt_gen?temperature=0.7",
                                                             data=json_data).json()
        print("mid_gen time elapsed %.2f seconds" % (time.time() - ts_start))

    session_state.status.prompts_generated = True


