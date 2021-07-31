from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import List
from uuid import UUID

from mimesis import Person, Text, Numbers, Datetime

from domain.classroom.classroom import Classroom, Duration, Attendee
from domain.client.client import Client
from domain.repository import Repository
from infrastructure.repository.memory.memory_client_repository import MemoryClientRepository
from web.schema.classroom_schemas import TimeUnit, AttendeeSchema, ClassroomPatch


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


class ClientJsonBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        person:Person = Person()
        self.firstname = person.first_name()
        self.lastname = person.last_name()

    def build(self):
        client = {"firstname": self.firstname, "lastname": self.lastname}
        return client


class ClassroomBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        self.name: str = Text().title()
        self.position: int = Numbers().integer_number(1, 6)
        self.start_date: datetime = Datetime().datetime()
        self.stop_date: datetime = None
        self.duration = Duration(TimeUnit.HOUR, 1)
        self.attendees = []

    def build(self) -> Classroom:
        classroom = Classroom.create(self.name, self.start_date, self.position, self.stop_date, self.duration)
        if self.attendees:
            classroom.set_attendees(self.attendees)
        return classroom

    def with_position(self, position: int) -> ClassroomBuilderForTest:
        self.position = position
        return self

    def with_attendee(self, client_id: UUID) -> ClassroomBuilderForTest:
        self.attendees.append(Attendee(client_id))
        return self


class ClassroomContextBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        self.repository = MemoryClientRepository()
        self.classrooms: List[Classroom] = []

    def build(self):
        return self.repository, self.classrooms

    def persist(self, repository: Repository = None) -> ClassroomContextBuilderForTest:
        if repository:
            self.repository = repository
        for client in self.classrooms:
            self.repository.persist(client)
        return self

    def with_one_classroom(self) -> ClassroomContextBuilderForTest:
        self.classrooms.append(ClassroomBuilderForTest().build())
        return self

    def with_classroom(self, classroom: Classroom) -> ClassroomContextBuilderForTest:
        self.classrooms.append(classroom)
        return self


class ClassroomJsonBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        self.classroom_name: str = Text().title()
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


class ClassroomPatchJsonBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        self.attendees = []

    def build(self):
        return ClassroomPatch.parse_obj({"attendees": self.attendees})

    def with_attendee(self, client_id) -> ClassroomPatchJsonBuilderForTest:
        self.attendees.append(AttendeeSchema.parse_obj({"client_id": client_id}))
        return self