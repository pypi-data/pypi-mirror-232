from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Union

from langchain.chains import LLMChain

from inarrator.email.message import IMessage


class ISummarizer(ABC):
    def __init__(self, api_token: str, model_name: str):
        """
        Abstract base class for summarizers.

        Args:
            api_token (str): The API token for the summarization model.
            model_name (str): The name of the summarization model.
        """
        self.chain = self.load_chain(api_token, model_name)

    @classmethod
    @abstractmethod
    def load_chain(self, api_token: str, model_name: str) -> LLMChain:
        """Load a language model chain for summarization.

        Args:
            api_token (str): The API token for the summarization model.
            model_name (str): The name of the summarization model.

        Returns:
            LLMChain: A language model chain for summarization.
        """
        pass

    @abstractmethod
    def summarize(self, messages: Union[IMessage, List[IMessage]]) -> str:
        """Summarize one or more email messages using the loaded language model chain.

        Args:
            message (Union[IMessage, List[IMessage]]): An email message or a list of email messages
            to be summarized.

        Returns:
            str: The summarized content of the message.
        """
        pass
