import streamlit as st

from digiprod_gen.backend.image import conversion
from digiprod_gen.backend.models.session import SessionState
from digiprod_gen.backend.utils.helper import Timer
from digiprod_gen.frontend.tab.image_generation.image_editing import set_image_pil_generated_by_user, \
    display_image_editor
from digiprod_gen.frontend.tab.image_generation.image_generation import update_session_selected_prompt, \
    display_image_generation_prompt, display_image_generator
from digiprod_gen.frontend.tab.image_generation.selected_products import display_mba_selected_products


def display_tab_image_gen_views(session_state: SessionState):
    if session_state.status.detail_pages_crawled:
        display_mba_selected_products(session_state.crawling_data, shirts_per_row=session_state.config.view.cards_per_row)

        if session_state.status.prompts_generated:
            predicted_prompts = session_state.image_gen_data.image_gen_prompts
            st.subheader("Suggested Prompts")
            st.write(predicted_prompts)

            st.subheader("Prepare Image for MBA Upload")
            st.markdown(
                "Please either generate the image directly or use one of the example Prompts to generate an image with SDXL or Dalle-3. \nYou can upload the image afterwards and proceed.")

            if session_state.image_gen_data.image_gen_prompts:
                index_list = [i for i, _ in enumerate(session_state.image_gen_data.image_gen_prompts)]
            else:
                index_list = [0]
            prompt_index = st.selectbox('Select a Prompt', index_list, on_change=update_session_selected_prompt, args=(session_state.image_gen_data,None,True,), key="selected_prompt_index")
            display_image_generation_prompt(session_state.image_gen_data, selected_prompt_index=prompt_index)
            display_image_generator(session_state)
        else:
            st.warning('Please click on 3. Prompt Generation')

    if not session_state.status.prompts_generated:
        # display image generation prompt with empty text field for image editor functionality
        display_image_generation_prompt(session_state.image_gen_data)


    set_image_pil_generated_by_user(session_state.image_gen_data)
    if session_state.image_gen_data.image_pil_generated:
        with Timer("display_image_editor"):
           image_pil_upload_ready = display_image_editor(session_state.image_gen_data, session_state.config.image_gen.background_removal, session_state.backend_caller)
        # Update session upload ready image
        if image_pil_upload_ready:
            session_state.image_gen_data.image_pil_upload_ready = conversion.ensure_rgba(conversion.pil2pil_png(image_pil_upload_ready))
