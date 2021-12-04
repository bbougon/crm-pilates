from __future__ import annotations

from typing import List

from domain.classroom.classroom_type import ClassroomType
from domain.commands import ClientCredits
from domain.repository import AggregateRoot


class Credits:

    def __init__(self, nb_credits: int, type: ClassroomType) -> None:
        self.__value = nb_credits
        self.__type = type

    @property
    def value(self):
        return self.__value

    @property
    def type(self):
        return self.__type

    def add(self, value: int):
        self.__value += value


class Client(AggregateRoot):

    def __init__(self, firstname: str, lastname: str):
        super().__init__()
        self.firstname = firstname
        self.lastname = lastname
        self.credits: List[Credits] = []

    def _provide_credits(self, client_credits: List[ClientCredits]):
        self.credits.extend(list(map(lambda credit: Credits(credit.value, credit.type), client_credits)))

    @staticmethod
    def create(firstname: str, lastname: str, client_credits: List[ClientCredits] = None) -> Client:
        client = Client(firstname, lastname)
        if client_credits:
            client._provide_credits(client_credits)
        return client

    def add_credits(self, credits: List[ClientCredits]):
        for client_credits in credits:
            found_credits = filter(lambda credit: credit.type is client_credits.type, self.credits)
            found_credit = next(found_credits, None)
            if found_credit:
                found_credit.add(client_credits.value)
            else:
                self._provide_credits([client_credits])
