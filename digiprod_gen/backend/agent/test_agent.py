import os
import time
import streamlit as st
import logging
import random
from functools import partial
from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools.render import format_tool_to_openai_function
from langchain.tools import StructuredTool
from langchain_openai import ChatOpenAI



from digiprod_gen.backend.agent.tools.product import (
    select_random_mba_products,
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
from digiprod_gen.backend.agent.constants import NICHES
from digiprod_gen.backend.agent.tools.upload import export_upload_data, check_run_id_done
from digiprod_gen.backend.agent.memory.container import global_memory_container


logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
logger.setLevel(logging.WARNING)  # or any variant from ERROR, CRITICAL or NOTSET
logger = logging.getLogger('seleniumwire')
logger.setLevel(logging.ERROR)  # Run selenium wire at ERROR level

def init_environment():
    os.environ["OPENAI_API_KEY"] = st.secrets["api_token"]["open_ai"]
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["api_token"]["replicate"]
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = "MBA_Agent"
    assert os.environ.get("LANGCHAIN_API_KEY", None), "'LANGCHAIN_API_KEY' does not exist in environment"


#backend_caller = BackendCaller(CONFIG.backend)
#crawl_mba_tool = StructuredTool.from_function(partial(crawl_mba, backend_caller=backend_caller))
# crawl_mba_tool = StructuredTool.from_function(func=lambda kwargs: crawl_mba(**kwargs, backend_caller=backend_caller),
#                                               name="crawlMBATool",
#                                               description="use to crawl amazon mba and receive mba products",
#                                               args_schema=CrawlingMBARequest)

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

if __name__ == "__main__":
    init_environment()

    from langchain import hub
    from langchain.agents import AgentExecutor, create_openai_tools_agent, create_openai_functions_agent
    #from langchain_community.chat_models import ChatOpenAI
    # Get the prompt to use - you can modify this!
    prompt: object = hub.pull("hwchase17/openai-tools-agent")
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.3)
    #llm = ChatOpenAI(model="gpt-4-1106-preview", temperature=0)
    # Construct the OpenAI Tools agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    #agent = create_openai_tools_agent(llm, tools, prompt)
    # Create an agent executor by passing in the agent and tools
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)


    # llm = OpenAI(model_name="gpt-4-1106-preview", temperature=0)
    # agent_executor = initialize_agent(
    #     tools,
    #     llm,
    #     agent=AgentType.OPENAI_MULTI_FUNCTIONS,
    #     verbose=True
    # )
    from copy import deepcopy
    search_terms = deepcopy(NICHES)
    random.shuffle(search_terms)
    # search_terms = ["Unicorn Metal"]
    for search_term in search_terms:
        global_memory_container.clear_memory()
        #search_term = "that you think is suitable for a print on demand niche"
        prompt = f"""
        Your final task is to create a new mba_product called product x.
        Create a mba request with search term '{search_term}' and crawl a list of mba_products.
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
        #     prompt = """Create and export a new mba_product.
        # Check at the end if you are done with the Tool checkRunIsDone and if not, make sure to export the final product correctly."""
        #prompt="""Crawl and select 2 mba_products with the search_term 'Unicorn metal'. Generate a image with the prompt 'Unicorn metal black background' and export the final generated mba product"""
        #
        ts = time.time()
        agent_executor.invoke({"input": prompt})
        print("Time elapsed in seconds %.2f seconds" % (time.time() - ts))

        #print(agent.agent.llm_chain.prompt.template)
        #print(agent_executor.run("Crawl some mba products and select 4 which you find suitable."))




