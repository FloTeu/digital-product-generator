from typing import List
from langchain.base_language import BaseLanguageModel
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate

from llm_few_shot_gen.generators.base import BaseFewShotGenerator
from llm_few_shot_gen.generators.midjourney import MidjourneyPromptGenerator
from llm_few_shot_gen.constants import INSTRUCTOR_USER_NAME
from digiprod_gen.backend.data_classes.mba import MBAMarketplaceDomain
from digiprod_gen.backend.generative_ai.text import mba_context
from digiprod_gen.backend.data_classes.mba import MBAProductTextType
from digiprod_gen.backend.data_classes.mba import MBAProduct
from digiprod_gen.backend.generative_ai.text.mba_banned_word import MBA_BANNED_WORDS

def get_generate_bullets_text(marketplace: MBAMarketplaceDomain, max_number_chars) -> str:
    if marketplace in [MBAMarketplaceDomain.COM, MBAMarketplaceDomain.UK]:
        return f"I need you to create six similar but not the same bullet texts with a maximum of {max_number_chars} chars. Write the answer in english."
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


class ProductTextGenerator(BaseFewShotGenerator):

    def _set_system_instruction(self):
        """Extends self.messages with instruction and type SystemMessagePromptTemplate"""
        self.messages.instruction = SystemMessagePromptTemplate.from_template("""
            You are a helpful assistant in helping me create Amazon MBA Product texts like bullet points, title, brand.
            MBA stands for Merch by Amazon, which is an on-demand t-shirt printing service.
            """)

    def _set_context(self):
        """Extends self.messages with context and type List[SystemMessagePromptTemplate]"""
        context_messages = []
        context_messages.append(SystemMessagePromptTemplate.from_template(
            f"""Here is some information about MBA product bullet points.
                {mba_context.mba_bullet_point_suggestion}
            """,
            additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
        context_messages.append(SystemMessagePromptTemplate.from_template(
            f"""Here is some information about MBA product title.
                {mba_context.mba_title_suggestion}
            """,
            additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
        context_messages.append(SystemMessagePromptTemplate.from_template(
            f"""Here is some information about MBA product brand.
                {mba_context.mba_brand_suggestion}
            """,
            additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
        self.messages.context = context_messages

    def set_few_shot_examples(self, few_shot_examples: List[str], mba_text_type: MBAProductTextType):
        messages = [SystemMessagePromptTemplate.from_template(
            f"Here are some example {mba_text_type}s. Try to understand the underlying format in order to create new creative {mba_text_type}s yourself later. ",
            additional_kwargs={"name": INSTRUCTOR_USER_NAME})]
        for i, example_prompt in enumerate(few_shot_examples):
            messages.append(
                SystemMessagePromptTemplate.from_template(f'Prompt {i}: "{example_prompt}". ',
                                                          additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
        self.messages.few_shot_examples = messages

    def _set_io_prompt(self, mba_text_type: MBAProductTextType, marketplace: MBAMarketplaceDomain):
        """Human message which contains the input for the text generation"""
        human_template = f"Do not include any of the following words: {MBA_BANNED_WORDS}.\n"
        if mba_text_type == MBAProductTextType.BULLET:
            human_template = human_template + get_generate_bullets_text(marketplace, 256)
        if mba_text_type == MBAProductTextType.BRAND:
            human_template = human_template + get_generate_brand_text(marketplace, 50)
        if mba_text_type == MBAProductTextType.TITLE:
            human_template = human_template + get_generate_title_text(marketplace, 50)
        self.messages.io_prompt = HumanMessagePromptTemplate.from_template(human_template)

class MBAMidjourneyPromptGenerator(MidjourneyPromptGenerator):

    def _set_io_prompt(self):
        """Human message which contains the input for the text generation"""
        human_template = """
                            I want you to act as a professional merch by amazon image creator.
                            Write five concise english prompts for the text delimited by ```.
                            The output prompt should focus on visual descriptions.
                            Take inspiration from the formating from the example prompts, dont copy them, but use the same format.
                            ```{text}```
                         """
        self.messages.io_prompt = HumanMessagePromptTemplate.from_template(human_template)