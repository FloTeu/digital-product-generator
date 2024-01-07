import os
import streamlit as st
import logging
from functools import partial
from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools.render import format_tool_to_openai_function
from langchain.tools import StructuredTool

from digiprod_gen.backend.agent.tools.product import (
    select_random_mba_products,
    print_select_mba_products,
    select_mba_products,
    generate_image,
    get_prompt_suggestions,
    evaluate_image,
    enrich_mba_products_with_image_caption)
from digiprod_gen.backend.agent.tools.crawling import crawl_overview_mba, crawl_products_detail_mba
from digiprod_gen.backend.agent.tools.upload import export_upload_data
from digiprod_gen.backend.agent.models.api import CrawlingMBARequest
from digiprod_gen.backend.api.common import CONFIG
from digiprod_gen.frontend.backend_caller import BackendCaller

logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
logger.setLevel(logging.WARNING)  # or any variant from ERROR, CRITICAL or NOTSET
logger = logging.getLogger('seleniumwire')
logger.setLevel(logging.ERROR)  # Run selenium wire at ERROR level

def init_environment():
    os.environ["OPENAI_API_KEY"] = st.secrets["api_token"]["open_ai"]
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["api_token"]["replicate"]


#backend_caller = BackendCaller(CONFIG.backend)
#crawl_mba_tool = StructuredTool.from_function(partial(crawl_mba, backend_caller=backend_caller))
# crawl_mba_tool = StructuredTool.from_function(func=lambda kwargs: crawl_mba(**kwargs, backend_caller=backend_caller),
#                                               name="crawlMBATool",
#                                               description="use to crawl amazon mba and receive mba products",
#                                               args_schema=CrawlingMBARequest)

tools = [
    #select_mba_products,
    generate_image,
    evaluate_image,
    get_prompt_suggestions,
    enrich_mba_products_with_image_caption,
    select_random_mba_products,
    print_select_mba_products,
    crawl_overview_mba,
    crawl_products_detail_mba,
    export_upload_data
]

if __name__ == "__main__":
    init_environment()

    from langchain import hub
    from langchain.agents import AgentExecutor, create_openai_tools_agent, create_openai_functions_agent
    from langchain_community.chat_models import ChatOpenAI
    # Get the prompt to use - you can modify this!
    prompt: object = hub.pull("hwchase17/openai-tools-agent")
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
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
    search_term = "Unicorn metal blegh"
    prompt = f"""
    Create a mba request with search term '{search_term}' and crawl a list of mba_products.
    Select a subsample of 2 products of the mba_products that you have received previously.
    Crawl detail information of your subsample.
    Enrich the subsample with image captions.
    Get some prompt suggestions choose the one which you find most suitable to create an image which sells well as print on demand product.
    Take your chosen prompt and create an image.
    Assess whether the image is suitable for a print-on-demand design and, depending on the answer, recreate the image or consider a different prompt.
    You can also slightly edit the prompt based on the feedback you got.
    Export the final generated mba product.
    """
    #prompt="""Crawl and select 2 mba_products with the search_term 'Unicorn metal'. Generate a image with the prompt 'Unicorn metal black background' and export the final generated mba product"""
    #
    agent_executor.invoke({"input": prompt})

    #print(agent.agent.llm_chain.prompt.template)
    #print(agent_executor.run("Crawl some mba products and select 4 which you find suitable."))




