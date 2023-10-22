from abc import abstractmethod
from typing import TypedDict


class Body(TypedDict):
    pass


class Message(TypedDict):
    to: str
    body: Body


class MessageNotifier:
    @abstractmethod
    def send(self, message: Message):
        pass
