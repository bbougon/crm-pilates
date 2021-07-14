from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import List
from uuid import UUID

from mimesis import Person, Text, Numbers, Datetime

from domain.client.client import Client
from domain.repository import Repository
from infrastructure.repository.memory.memory_client_repository import MemoryClientRepository
from web.schema.classroom_creation import TimeUnit


class Builder:
    @abstractmethod
    def build(self):
        ...


class ClientBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        person = Person()
        self.firstname = person.last_name()
        self.lastname = person.first_name()

    def build(self) -> Client:
        return Client.create(self.firstname, self.lastname)


class ClientContextBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        self.repository = MemoryClientRepository()
        self.clients: List[Client] = []

    def build(self):
        return self.repository, self.clients

    def with_clients(self, number_of_clients: int) -> ClientContextBuilderForTest:
        for i in range(number_of_clients):
            self.clients.append(ClientBuilderForTest().build())
        return self

    def persist(self, repository: Repository = None) -> ClientContextBuilderForTest:
        if repository:
            self.repository = repository
        for client in self.clients:
            self.repository.persist(client)
        return self

    def with_one_client(self) -> ClientContextBuilderForTest:
        return self.with_clients(1)


class ClassroomJsonBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        self.classroom_name: str = Text().text(1)
        self.position: int = Numbers().integer_number(1, 6)
        self.start_date: datetime = Datetime().datetime()
        self.stop_date: datetime = None
        self.attendees: List[UUID] = []
        self.duration: dict = None

    def build(self):
        classroom = {"name": self.classroom_name, "position": self.position, "start_date": self.start_date.isoformat()}
        if self.attendees:
            classroom["attendees"] = list(map(lambda attendee: {"client_id": attendee.hex},self.attendees))
        if self.stop_date:
            classroom["stop_date"] = self.stop_date
        if self.duration:
            classroom["duration"] = self.duration
        return classroom

    def with_attendees(self, attendees: List[UUID]) -> ClassroomJsonBuilderForTest:
        self.attendees.extend(attendees)
        return self

    def with_start_date(self, start_date: datetime) -> ClassroomJsonBuilderForTest:
        self.start_date = start_date
        return self

    def with_stop_date(self, stop_date: datetime) -> ClassroomJsonBuilderForTest:
        self.stop_date = stop_date
        return self

    def with_name(self, name: str) -> ClassroomJsonBuilderForTest:
        self.classroom_name = name
        return self

    def with_position(self, position: int) -> ClassroomJsonBuilderForTest:
        self.position = position
        return self

    def with_duration(self, duration: int, time_unit: TimeUnit) -> ClassroomJsonBuilderForTest:
        self.duration = {"duration": duration, "unit": time_unit.value}
        return self
