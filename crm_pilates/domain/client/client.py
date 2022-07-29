from __future__ import annotations

from typing import List

from crm_pilates.domain.classroom.classroom_type import ClassroomSubject
from crm_pilates.domain.commands import ClientCredits
from crm_pilates.domain.exceptions import DomainException
from crm_pilates.domain.repository import AggregateRoot


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

    def refund(self):
        self.__value += 1

    def add_credits(self, value: int):
        self.__value += value


class Client(AggregateRoot):
    def __init__(self, firstname: str, lastname: str):
        super().__init__()
        self.firstname = firstname
        self.lastname = lastname
        self.credits: List[Credits] = []

    def _add_credits(self, client_credits: List[ClientCredits]):
        for _client_credits in client_credits:
            existing_credits = next(
                filter(
                    lambda credits: credits.subject is _client_credits.subject,
                    self.credits,
                ),
                None,
            )
            existing_credits.add_credits(
                _client_credits.value
            ) if existing_credits else self.credits.append(
                Credits(_client_credits.value, _client_credits.subject)
            )

    @staticmethod
    def create(
        firstname: str, lastname: str, client_credits: List[ClientCredits] = None
    ) -> Client:
        client = Client(firstname, lastname)
        if client_credits:
            client._add_credits(client_credits)
        return client

    def add_credits(self, credits: List[ClientCredits]):
        self._add_credits(credits)

    def decrease_credits_for(self, subject: ClassroomSubject):
        available_credits: Credits = next(
            filter(lambda credit: credit.subject is subject, self.credits), None
        )
        if not available_credits:
            available_credits = Credits(0, subject)
            self.credits.append(available_credits)
        available_credits.decrease()

    def refund_credits_for(self, subject: ClassroomSubject):
        available_credits: Credits = next(
            filter(lambda credit: credit.subject is subject, self.credits), None
        )
        if not available_credits:
            raise DomainException(
                f"Credits for client with id '{str(self.id)}' cannot be refund as the client has no credits available."
            )
        available_credits.refund()
