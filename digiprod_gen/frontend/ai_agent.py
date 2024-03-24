import streamlit as st
import time

from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent, create_openai_functions_agent
from langchain_community.chat_models.openai import ChatOpenAI

from digiprod_gen.backend.agent.memory import global_memory_container
from digiprod_gen.backend.models.session import SessionState, CrawlingData
from digiprod_gen.frontend.session import update_mba_request
from digiprod_gen.backend.agent.tools.product import (
    print_select_mba_products,
    select_mba_products,
    generate_image,
    get_prompt_suggestions,
    evaluate_image,
    extract_keywords,
    select_mba_listings,
    generate_listing_suggestions,
    enrich_mba_products_with_image_caption)
from digiprod_gen.backend.agent.tools.crawling import crawl_overview_mba, crawl_products_detail_mba, get_random_search_term
from digiprod_gen.backend.agent.tools.upload import export_upload_data, check_run_id_done
from digiprod_gen.frontend.agent_callbacks import AiAgentFrontendCallbackHandler

tools = [
    select_mba_products,
    #select_random_mba_products,
    generate_image,
    evaluate_image,
    get_prompt_suggestions,
    select_mba_listings,
    enrich_mba_products_with_image_caption,
    print_select_mba_products,
    check_run_id_done,
    get_random_search_term,
    crawl_overview_mba,
    crawl_products_detail_mba,
    generate_listing_suggestions,
    export_upload_data,
    extract_keywords
]

def run_ai_agent_product_generation():
    """
    Takes a search term runs an ai agent with the following steps:
        1. Crawling
        2. Select matching designs
        3. Prompt generation
        4. Image generation
        5. Export to file system
    """
    session_state: SessionState = st.session_state["session_state"]

    # If not set yet, init session request
    if session_state.crawling_request == None:
        update_mba_request()


    prompt: object = hub.pull("hwchase17/openai-tools-agent")
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.3)
    # Construct the OpenAI Tools agent
    tools = [crawl_overview_mba, select_mba_products, crawl_products_detail_mba]
    agent = create_openai_functions_agent(llm, tools, prompt)
    # Create an agent executor by passing in the agent and tools
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    global_memory_container.clear_memory()
    # search_term = "that you think is suitable for a print on demand niche"
    prompt = f"""
    Your final task is to create a new mba_product called product x.
    Create a mba request with search term '{session_state.crawling_request.search_term}' in a suitable marketplace and crawl a list of mba_products.
    Select a subsample of 2 products of the mba_products that you have received previously.
    Crawl detail information of your subsample.
    Extract keywords from the selected subsample.
    Create listing suggestions for title, brand and bullets for product x.
    Enrich the subsample with image captions.
    Get some prompt suggestions and choose the one which you find most suitable to create an image which sells well as print on demand product.
    Take your chosen prompt and create an image.
    Assess whether the image is suitable for a print-on-demand design and, depending on the answer, recreate the image or consider a different prompt.
    You can also slightly edit the prompt based on the feedback you got.
    Choose the best title, brand and bullets from your received suggestions with the function selectMBAListingsTool.
    Export the final product x.
    Call checkRunIsDone at the end and check if your done. If the response is not successful, please fix what is missing.
    """
    prompt = "Crawl mba products select a subsample of 2 products and crawl the detail information"
    #     prompt = """Create and export a new mba_product.
    # Check at the end if you are done with the Tool checkRunIsDone and if not, make sure to export the final product correctly."""
    # prompt="""Crawl and select 2 mba_products with the search_term 'Unicorn metal'. Generate a image with the prompt 'Unicorn metal black background' and export the final generated mba product"""
    #
    ts = time.time()
    config = {"callbacks": [AiAgentFrontendCallbackHandler()]}
    agent_executor.invoke({"input": prompt}, config=config)
    print("Time elapsed in seconds %.2f seconds" % (time.time() - ts))