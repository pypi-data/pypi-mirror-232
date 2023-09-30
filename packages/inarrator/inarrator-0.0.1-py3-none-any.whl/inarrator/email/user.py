import concurrent.futures
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Dict, List, Sequence, Tuple

from inarrator.email.email import IEmail
from inarrator.email.message import IMessage
from inarrator.exceptions import AuthenticationError


class IUser(ABC):
    def __init__(self, emails: List[IEmail]):
        self.emails = emails

    @abstractmethod
    def authenticate(self) -> None:
        """Authentication of each email API for the given user."""
        pass

    @classmethod
    @abstractmethod
    def read_email_specific_client(
        cls, email: IEmail, **kwargs: Any
    ) -> Tuple[str, Sequence[IMessage]]:
        """Reads  the user email for the specific email client.

        Args:
        ----
            email: IEmail Instance.

            kwargs: Keyword Argument be used when fetching the email for the given client

        Returns:
        -------
            A tuple consist of IEmail child class name and sequence of fetched messages.

        """

        pass

    @abstractmethod
    def read_latest_emails(self, **kwargs: Any) -> Dict[str, Sequence[IMessage]]:
        """Getting the latest unread emails for a user in a parallel manner.
        Spawns multiple processors to fetch emails from each of the email client for
        the given user in a parallel manner.

        Args:
        ----
            kwargs: Keyword Argument be used when fetching the emails.

        Returns:
        -------
            A dictionary which consist of emails provider and messages from each email provider
        """
        pass

    @abstractmethod
    def summarize_latest_emails(self) -> str:
        pass


class User(IUser):
    def __init__(self, emails: List[IEmail]):
        self.emails = emails

    def authenticate(self) -> None:
        for email in self.emails:
            if not email.service:
                raise AuthenticationError(
                    f"""Authentication Error.
                    Make sure following {email._type} API has not been authenticated
                    """
                )

    @classmethod
    def read_email_specific_client(
        cls, email: IEmail, **kwargs: Any
    ) -> Tuple[str, Sequence[IMessage]]:
        return email._type, email.get_latest_emails(**kwargs)

    def read_latest_emails(self, **kwargs: Any) -> Dict[str, Sequence[IMessage]]:
        emails_dict = {}
        with ProcessPoolExecutor() as executor:
            email_futures = [
                executor.submit(User.read_email_specific_client, email, **kwargs)
                for email in self.emails
            ]
        for future in concurrent.futures.as_completed(email_futures):
            email_type, latest_emails = future.result()
            emails_dict[email_type] = latest_emails

        return emails_dict

    def summarize_latest_emails(self) -> str:
        return ""
