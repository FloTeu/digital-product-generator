import streamlit as st
from typing import Any, Optional
from uuid import UUID

from langchain.callbacks.base import BaseCallbackHandler
from langchain.tools import ShellTool
from langchain_core.agents import AgentAction, AgentFinish

from digiprod_gen.backend.agent.memory import global_memory_container
from digiprod_gen.backend.agent.models.memory import MemoryId
from digiprod_gen.backend.models.session import SessionState
from digiprod_gen.frontend.session import read_session, ai_agent_update_mba_products, \
    ai_agent_update_selected_mba_products, ai_agent_update_selected_mba_products_details_crawled, \
    ai_agent_update_listing, ai_agent_update_prompt_suggestions, ai_agent_update_image_generation
from digiprod_gen.frontend.tab.crawling.tab_crawling import display_mba_overview_products
from digiprod_gen.frontend.tab.image_generation.views import display_tab_image_gen_views
from digiprod_gen.frontend.tab.upload.views import display_tab_upload_views


class AiAgentFrontendCallbackHandler(BaseCallbackHandler):
    def __init__(self, *args, **kwargs):
        self.session_state: SessionState = read_session("session_state")
        self.st_agent_view = self.session_state.views.get_or_create_ai_agent()
        super().__init__(*args, **kwargs)

    def on_tool_start(self, serialized, input_str: str, **kwargs):
        """Run when tool starts running."""
        print("ON TOOL START!")

    def on_tool_end(self, output: str, **kwargs):
        """Run when tool ends running."""
        ai_agent_view_text: str = ""
        if kwargs.get("name") == "crawlOverviewMBATool":
            ai_agent_view_text = "MBA products crawled!"
            ai_agent_update_mba_products(self.session_state)

            with self.session_state.views.tabs.crawling:
                overview_designs_view = self.session_state.views.get_or_create_overview_designs()
                # before re rendering, empty all existing elements in view
                overview_designs_view.empty()

                # Render frontend updates
                with overview_designs_view.container():
                    if self.session_state.status.overview_page_crawled:
                        display_mba_overview_products(self.session_state.crawling_data,
                                                      self.session_state.crawling_request,
                                                      shirts_per_row=self.session_state.config.view.cards_per_row)

        if kwargs.get("name") == "selectMBAProductsTool":
            ai_agent_view_text = "MBA products selected!"
            ai_agent_update_selected_mba_products(self.session_state)

        if kwargs.get("name") == "crawlProductsMBATool":
            ai_agent_view_text = "MBA selected products crawled!"
            ai_agent_update_selected_mba_products_details_crawled(self.session_state)

            # Render frontend updates
            with self.session_state.views.tabs.image_gen:
                display_tab_image_gen_views(self.session_state)

        if kwargs.get("name") == "enrichMBAProductsWithImageCaptionTool":
            ai_agent_view_text = "MBA selected products enriched with image caption!"
            ai_agent_update_selected_mba_products_details_crawled(self.session_state)

            # Render frontend updates
            with self.session_state.views.tabs.image_gen:
                display_tab_image_gen_views(self.session_state)


        if kwargs.get("name") == "getPromptSuggestionsTool":
            ai_agent_view_text = "Image prompt suggestions generated!"
            ai_agent_update_prompt_suggestions(self.session_state)

            # Render frontend updates
            with self.session_state.views.tabs.image_gen:
                display_tab_image_gen_views(self.session_state)

        if kwargs.get("name") == "generateImageTool":
            ai_agent_view_text = "Image generated!"
            ai_agent_update_image_generation(self.session_state)

            # Render frontend updates
            with self.session_state.views.tabs.image_gen:
                display_tab_image_gen_views(self.session_state)

        if kwargs.get("name") == "generateListingSuggestions":
            if all(memory_key in global_memory_container for memory_key in
                   [MemoryId.BRAND_SUGGESTIONS, MemoryId.TITLE_SUGGESTIONS, MemoryId.BULLET_SUGGESTIONS]):
                ai_agent_view_text = "MBA listings generated!"
                ai_agent_update_listing(self.session_state)

                # Render frontend updates
                with self.session_state.views.tabs.upload:
                    display_tab_upload_views(self.session_state)

        # TODO: Ensure information is visible for the user (i.e. at the bottom of the page)
        with self.st_agent_view.container():
            st.write(ai_agent_view_text)
            print(ai_agent_view_text)

    def on_agent_finish(
            self,
            finish: AgentFinish,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            **kwargs: Any,
    ) -> Any:
        """Run on agent end."""
        print("Agent has finishes")
