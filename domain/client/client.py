from __future__ import annotations

from typing import List

from domain.classroom.classroom_type import ClassroomSubject
from domain.commands import ClientCredits
from domain.repository import AggregateRoot


class Credits:

    def __init__(self, nb_credits: int, subject: ClassroomSubject) -> None:
        self.__value = nb_credits
        self.__subject = subject

    @property
    def value(self):
        return self.__value

    @property
    def subject(self):
        return self.__subject

    def decrease(self):
        self.__value -= 1


class Client(AggregateRoot):

    def __init__(self, firstname: str, lastname: str):
        super().__init__()
        self.firstname = firstname
        self.lastname = lastname
        self.credits: List[Credits] = []

    def _provide_credits(self, client_credits: List[ClientCredits]):
        self.credits = (list(map(lambda credit: Credits(credit.value, credit.subject), client_credits)))

    @staticmethod
    def create(firstname: str, lastname: str, client_credits: List[ClientCredits] = None) -> Client:
        client = Client(firstname, lastname)
        if client_credits:
            client._provide_credits(client_credits)
        return client

    def add_credits(self, credits: List[ClientCredits]):
        self._provide_credits(credits)
