from __future__ import annotations

from abc import ABC
from typing import List, Union

from langchain.chains import LLMChain
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate

from inarrator.email.message import IMessage
from inarrator.summarizer.prompt import HUGGING_FACE_EMAIL_PROMPT


class HuggingFaceModel(ABC):
    def __init__(self, api_token: str, model_name: str):
        self.chain = self.load_chain(api_token, model_name)

    @classmethod
    def load_chain(self, api_token: str, model_name: str) -> LLMChain:
        return LLMChain(
            llm=HuggingFaceHub(huggingfacehub_api_token=api_token, repo_id=model_name),
            prompt=PromptTemplate(
                template=HUGGING_FACE_EMAIL_PROMPT, input_variables=["fro", "to", "subject", "body"]
            ),
        )

    def summarize(self, messages: Union[IMessage, List[IMessage]]) -> str:
        if isinstance(messages, list):
            raise ValueError(
                "HuggingFace Hub Model do not currently support summarizing multiple messages"
            )
        elif isinstance(messages, IMessage):
            return self.chain.predict(
                fro=messages.fro,
                to=messages.to,
                body=messages.body,
                subject=messages.subject,
            )
