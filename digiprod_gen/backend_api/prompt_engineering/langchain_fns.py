from typing import List
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.prompts.base import BasePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from digiprod_gen.backend_api.prompt_engineering.utils import get_midjourney_example_prompts

INSTRUCTOR_USER_NAME = "instructor"

def get_chat_gpt_model(temperature=0.7) -> ChatOpenAI:
    return ChatOpenAI(temperature=temperature, model_name="gpt-3.5-turbo")

def get_system_message_prompt_generator() -> SystemMessagePromptTemplate:
    return SystemMessagePromptTemplate.from_template("""
    You are a helpful assistant, who helps me creating text-to-image prompts.
    I want to sell t-shirt designs on the Merch by Amazon platform. Merch by Amazon is an on-demand t-shirt printing service.
    """)

def get_midjourney_instructions() -> List[BasePromptTemplate]:
    system_prompt_templates = []
    system_prompt_templates.append(SystemMessagePromptTemplate.from_template("Here is some general information about the Midjourney company. " + midjourney.midjourney_company_information, additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
    system_prompt_templates.append(SystemMessagePromptTemplate.from_template(midjourney.midjourney_v5_general_description, additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
    system_prompt_templates.append(SystemMessagePromptTemplate.from_template(midjourney.midjourney_v5_additional_description, additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
    system_prompt_templates.append(SystemMessagePromptTemplate.from_template("Now i will provide you some information about prompt engineering for Midjourney." + midjourney.prompt_general_desciption, additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
    system_prompt_templates.append(SystemMessagePromptTemplate.from_template(midjourney.prompt_length, additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
    system_prompt_templates.append(SystemMessagePromptTemplate.from_template(midjourney.prompt_grammer, additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
    system_prompt_templates.append(SystemMessagePromptTemplate.from_template(midjourney.prompt_what_you_want, additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
    system_prompt_templates.append(SystemMessagePromptTemplate.from_template(midjourney.prompt_details, additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
    system_prompt_templates.append(SystemMessagePromptTemplate.from_template("Here are some example Midjourney prompts for t-shirt design generations. ", additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
    return system_prompt_templates

def get_few_shot_midjourney_prompt_examples() -> List[BasePromptTemplate]:
    system_prompt_templates = []
    for i, example_prompt in enumerate(get_midjourney_example_prompts()):
        system_prompt_templates.append(SystemMessagePromptTemplate.from_template(f'Prompt {i}: "{example_prompt}". ', additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
    return system_prompt_templates

def get_midjourney_prompt_generator_chain(llm, multiple_suggestions=False) -> LLMChain:
    # Now i want you to act as a professional t-shirt design creator. You will use a rich and descriptive language when describing your design prompts. Take inspiration from the formating from the example prompts, dont copy them, but use the same format.
    human_template=f"""
                      Write {'a enumerated list of ' if multiple_suggestions else 'a'} prompt{'s starting with 1. with at leats 5 examples' if multiple_suggestions else ''} for the text delimited by ```. 
                      Consider everything you learned about prompting for Midjourney and only provide the final text-to-image prompt without further details.
                      You may receive some information regarding the target group of the product. Please ignore them for the final output prompt and only include visual aspects.
                    """
    human_template=human_template + "```{text}```"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    messages = [
        get_system_message_prompt_generator(),
        *get_midjourney_instructions(),
        *get_few_shot_midjourney_prompt_examples(),
        human_message_prompt
    ]
    chat_prompt = ChatPromptTemplate.from_messages(messages)
    return LLMChain(llm=llm, prompt=chat_prompt)
