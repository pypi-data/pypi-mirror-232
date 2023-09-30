from __future__ import annotations

from typing import List, Union

from langchain.chains import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from inarrator.email.message import IMessage
from inarrator.summarizer.base import ISummarizer
from inarrator.summarizer.prompt import STUFF_EMAIL_PROMPT


class GPTModel(ISummarizer):
    def __init__(self, api_token: str, model_name: str):
        self.chain = self.load_chain(api_token, model_name)

    @classmethod
    def load_chain(self, api_token: str, model_name: str) -> LLMChain:
        llm = ChatOpenAI(openai_api_key=api_token, model_name=model_name, temperature=0)
        prompt = PromptTemplate.from_template(STUFF_EMAIL_PROMPT)
        return load_summarize_chain(
            llm, prompt=prompt, chain_type="stuff", document_variable_name="emails"
        )

    def summarize(self, messages: Union[IMessage, List[IMessage]]) -> str:
        if isinstance(messages, IMessage):
            messages = [messages]
        messages = list(map(lambda x: x.message_to_document(), messages))
        return self.chain.run(messages)
