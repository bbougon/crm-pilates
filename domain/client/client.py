from __future__ import annotations
from domain.repository import AggregateRoot


class Client(AggregateRoot):

    def __init__(self, lastname: str, firstname:str):
        super().__init__()
        self.firstname = firstname
        self.lastname = lastname

    @staticmethod
    def create(firstname:str, lastname:str) -> Client:
        return Client(firstname, lastname)