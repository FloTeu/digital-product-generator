# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai
import sys
import streamlit as st
from typing import List

from digiprod_gen.backend.models.mba import MBAMarketplaceDomain, MBAProduct

sys.path.append("...")
from digiprod_gen.backend.prompt_engineering import get_midjourney_example_prompts

openai.api_key = st.secrets["open_ai_api_key"]

def get_instruction_text(marketplace: MBAMarketplaceDomain = MBAMarketplaceDomain.COM) -> str:
    #if marketplace in [MBAMarketplaceDomain.COM, MBAMarketplaceDomain.UK]:
    return "You are a helpful assistant, who helps me creating text-to-image prompts. I want to sell t-shirt designs on the Merch by Amazon platform. Merch by Amazon is an on-demand t-shirt printing service."
    #elif marketplace == MBAMarketplaceDomain.DE:
    #    return "Sie sind ein hilfreicher Assistent, der mir bei der Erstellung von text-to-image prompts hilft. Ich möchte T-Shirt-Designs über die Plattform Merch by Amazon verkaufen. Merch by Amazon ist ein Dienst zum Bedrucken von T-Shirts auf Abruf."

def get_instruction_midjourney_prompt_text() -> str:
    return "You are a helpful assistant, who helps me creating text-to-image prompts. I want to sell t-shirt designs on the Merch by Amazon platform. Merch by Amazon is an on-demand t-shirt printing service."


def get_did_you_understand_text(marketplace: MBAMarketplaceDomain = MBAMarketplaceDomain.COM) -> str:
    #if marketplace in [MBAMarketplaceDomain.COM, MBAMarketplaceDomain.UK]:
    return 'But wait i have more information. Just answer with READ'
    #elif marketplace == MBAMarketplaceDomain.DE:
    #    return 'Ich habe eine weitere Beschreibung für Sie. Wenn Sie verstanden haben, antworten Sie mit "Ja".'


def get_did_you_understand_response_text(marketplace: MBAMarketplaceDomain = MBAMarketplaceDomain.COM) -> str:
    #if marketplace in [MBAMarketplaceDomain.COM, MBAMarketplaceDomain.UK]:
    return "READ"
    #elif marketplace == MBAMarketplaceDomain.DE:
    #    return "Ja, Ich habe verstanden."

def get_generate_bullets_text(marketplace: MBAMarketplaceDomain, max_number_chars) -> str:
    if marketplace in [MBAMarketplaceDomain.COM, MBAMarketplaceDomain.UK]:
        return f"I need you to create six similar but not the same description texts with a maximum of {max_number_chars} chars. Write the answer in english."
    elif marketplace == MBAMarketplaceDomain.DE:
        return f'Erstelle mir sechs ähnliche, aber nicht identische Beschreibungstexte mit maximale {max_number_chars} Zeichen. Schreibe die Antwprt auf deutsch.'

def get_generate_title_text(marketplace: MBAMarketplaceDomain, max_number_chars) -> str:
    if marketplace in [MBAMarketplaceDomain.COM, MBAMarketplaceDomain.UK]:
        return f"I need you to create six similar but not the same product title texts with a maximum of {max_number_chars} chars. Write the answer in english."
    elif marketplace == MBAMarketplaceDomain.DE:
        return f'Erstelle mir sechs ähnliche, aber nicht identische Produkttitel mit maximale {max_number_chars} Zeichen. Schreibe die Antwprt auf deutsch.'

def get_generate_brand_text(marketplace: MBAMarketplaceDomain, max_number_chars) -> str:
    if marketplace in [MBAMarketplaceDomain.COM, MBAMarketplaceDomain.UK]:
        return f"I need you to create six similar but not the same product brand names with a maximum of {max_number_chars} chars. Write the answer in english."
    elif marketplace == MBAMarketplaceDomain.DE:
        return f'Erstelle mir sechs ähnliche, aber nicht identische Marken Namen mit maximale {max_number_chars} Zeichen. Schreibe die Antwprt auf deutsch.'


def get_openai_midjourney_instruction():
    midjourney_example_prompts = get_midjourney_example_prompts()
    messages = [
        {"role": "user",
         "content": "Here is some general information about Midjourney company. " + midjourney.midjourney_company_information + " " + get_did_you_understand_text()},
        {"role": "assistant",
         "content": get_did_you_understand_response_text()},
        {"role": "user",
         "content": midjourney.midjourney_v5_general_description + " " + get_did_you_understand_text() },
        {"role": "assistant",
         "content": get_did_you_understand_response_text()},
        {"role": "user",
         "content": midjourney.midjourney_v5_additional_description + " " + get_did_you_understand_text() },
        {"role": "assistant",
         "content": get_did_you_understand_response_text()},
        {"role": "user",
         "content": "Now i will provide you some information about prompt engineering for Midjourney. " + midjourney.prompt_general_desciption + " " + get_did_you_understand_text() },
        {"role": "assistant",
         "content": get_did_you_understand_response_text()},
        {"role": "user",
         "content": midjourney.prompt_length + " " + get_did_you_understand_text() },
        {"role": "assistant",
         "content": get_did_you_understand_response_text()},
        {"role": "user",
         "content": midjourney.prompt_grammer + " " + get_did_you_understand_text() },
        {"role": "assistant",
         "content": get_did_you_understand_response_text()},
        {"role": "user",
         "content": midjourney.prompt_what_you_want + " " + get_did_you_understand_text() },
        {"role": "assistant",
         "content": get_did_you_understand_response_text()},
        {"role": "user",
         "content": midjourney.prompt_details + " " + get_did_you_understand_text() },
        {"role": "assistant",
         "content": get_did_you_understand_response_text()},
        {"role": "user",
         "content": "Here are some example Midjourney prompts for t-shirt design generations. " + get_did_you_understand_text() },
        {"role": "assistant",
         "content": get_did_you_understand_response_text()},
    ]
    for i, example_prompt in enumerate(midjourney_example_prompts):
        messages.extend([
            {"role": "user",
             "content": f'Prompt {i}: "{example_prompt}". ' + get_did_you_understand_text() },
            {"role": "assistant",
             "content": get_did_you_understand_response_text()}
        ])
    return messages


def mba_products2midjourney_prompts(mba_products: List[MBAProduct]) -> List[str]:
    messages = [
        {"role": "system",
         "content": get_instruction_text()}
    ]
    messages.extend(get_openai_midjourney_instruction())
    all_bullets = []
    [all_bullets.extend(mba_product.bullets) for mba_product in mba_products]
    descriptions_text = "Description: " + "\nDescription: ".join(all_bullets)
    messages.extend([
        {"role": "user",
         "content": f"Now i want you to act as a professional t-shirt design creator. You will use a rich and descriptive language when describing your design prompts. Take inspiration from the formating from the example prompts, dont copy them, but use the same format. {get_did_you_understand_text()}"},
        {"role": "assistant",
         "content": get_did_you_understand_response_text()},
        {"role": "user",
         "content": f"Here are multiple descriptions of mba products, which i like you to transform into a enumerated list of prompts starting with 1.. Remember to format the prompts semantically similarly to the example prompts. {descriptions_text}."}
        #{"role": "assistant",
        # "content": get_did_you_understand_response_text()}
    ])

    open_ai_response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
    )
    prompt = open_ai_response["choices"][0]["message"].content
    # If gpt recommends multiple prompts, try to extract them
    number_indicator = [str(i) for i in range(10)]
    prompts = [p.replace("Prompt", "")[3:].strip('"').strip(':') for p in prompt.split("\n") if p[0:1] in number_indicator]
    return prompts if len(prompts) > 0 else [prompt]


def mba_products2bullets(mba_products: List[MBAProduct], marketplace: MBAMarketplaceDomain, max_number_chars=256) -> List[str]:
    messages = [
        {"role": "system",
         "content": get_instruction_text(marketplace=marketplace)}
    ]
    for mba_product in mba_products:
        for bullet in mba_product.bullets:
            messages.extend([
                {"role": "user",
                 "content": f"{bullet}. {get_did_you_understand_text(marketplace)}"},
                {"role": "assistant",
                 "content": get_did_you_understand_response_text(marketplace)}
            ])
    messages.append({"role": "user", "content": get_generate_bullets_text(marketplace, max_number_chars)})

    open_ai_response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
    )
    prompt = open_ai_response["choices"][0]["message"].content
    # If gpt recommends multiple prompts, try to extract them
    number_indicator = [str(i) for i in range(10)]
    prompts = [p[3:] for p in prompt.split("\n") if p[0:1] in number_indicator]
    prompts = prompts if len(prompts) > 0 else [prompt]
    assert all([len(prompt) <= max_number_chars for prompt in prompts]), f"Not all prompts have fewer than {max_number_chars} chars"
    return prompts


def mba_products2titles(mba_products: List[MBAProduct], marketplace: MBAMarketplaceDomain, max_number_chars=50) -> List[str]:
    messages = [
        {"role": "system",
         "content": get_instruction_text(marketplace=marketplace)}
    ]
    for mba_product in mba_products:
        title = mba_product.title.replace("T-Shirt", "")
        messages.extend([
            {"role": "user",
                "content": f"{title}. {get_did_you_understand_text(marketplace)}"},
            {"role": "assistant",
                "content": get_did_you_understand_response_text(marketplace)}
        ])
    messages.append({"role": "user", "content": get_generate_title_text(marketplace, max_number_chars)})

    open_ai_response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
    )
    prompt = open_ai_response["choices"][0]["message"].content
    # If gpt recommends multiple prompts, try to extract them
    number_indicator = [str(i) for i in range(10)]
    prompts = [p[3:] for p in prompt.split("\n") if p[0:1] in number_indicator]
    prompts = prompts if len(prompts) > 0 else [prompt]
    assert all([len(prompt) <= max_number_chars for prompt in prompts]), f"Not all prompts have fewer than {max_number_chars} chars"
    return prompts

def mba_products2brands(mba_products: List[MBAProduct], marketplace: MBAMarketplaceDomain, max_number_chars=50) -> List[str]:
    messages = [
        {"role": "system",
         "content": get_instruction_text(marketplace=marketplace)}
    ]
    for mba_product in mba_products:
        messages.extend([
            {"role": "user",
                "content": f"{mba_product.title}. {get_did_you_understand_text(marketplace)}"},
            {"role": "assistant",
                "content": get_did_you_understand_response_text(marketplace)}
        ])
    messages.append({"role": "user", "content": get_generate_brand_text(marketplace, max_number_chars)})

    open_ai_response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
    )
    prompt = open_ai_response["choices"][0]["message"].content
    # If gpt recommends multiple prompts, try to extract them
    number_indicator = [str(i) for i in range(10)]
    prompts = [p[3:] for p in prompt.split("\n") if p[0:1] in number_indicator]
    prompts = prompts if len(prompts) > 0 else [prompt]
    assert all([len(prompt) <= max_number_chars for prompt in prompts]), f"Not all prompts have fewer than {max_number_chars} chars"
    return prompts