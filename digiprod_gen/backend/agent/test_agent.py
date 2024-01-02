import os
import streamlit as st
from digiprod_gen.backend.agent.tools.product import select_mba_products, print_select_mba_products
from digiprod_gen.backend.agent.tools.crawling import get_crawling_request, crawl_mba
from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools.render import format_tool_to_openai_function


def init_environment():
    os.environ["OPENAI_API_KEY"] = st.secrets["api_token"]["open_ai"]
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["api_token"]["replicate"]

tools = [
    get_crawling_request,
    crawl_mba,
    select_mba_products,
    print_select_mba_products
]

if __name__ == "__main__":
    init_environment()

    from langchain import hub
    from langchain.agents import AgentExecutor, create_openai_tools_agent, create_openai_functions_agent
    from langchain_community.chat_models import ChatOpenAI
    # Get the prompt to use - you can modify this!
    prompt: object = hub.pull("hwchase17/openai-tools-agent")
    #llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
    llm = ChatOpenAI(model="gpt-4-1106-preview", temperature=0)
    # Construct the OpenAI Tools agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    #agent = create_openai_tools_agent(llm, tools, prompt)
    # Create an agent executor by passing in the agent and tools
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


    # llm = OpenAI(model_name="gpt-4-1106-preview", temperature=0)
    # agent_executor = initialize_agent(
    #     tools,
    #     llm,
    #     agent=AgentType.OPENAI_MULTI_FUNCTIONS,
    #     verbose=True
    # )

    agent_executor.invoke({"input": "Create a mba request with search term 'Unicorn' and crawl some mba products. Select a subsample by using one of your tools. Print selected subsample at the end."})

    #print(agent.agent.llm_chain.prompt.template)
    #print(agent_executor.run("Crawl some mba products and select 4 which you find suitable."))




