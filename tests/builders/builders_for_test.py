from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import List
from uuid import UUID

from mimesis import Person, Text, Numbers, Datetime

from domain.classroom.classroom import Classroom, Attendee
from domain.classroom.duration import Duration, HourTimeUnit
from domain.client.client import Client
from domain.repository import Repository
from infrastructure.repository.memory.memory_classroom_repositories import MemoryClassroomRepository
from infrastructure.repository.memory.memory_client_repositories import MemoryClientRepository
from web.schema.classroom_schemas import TimeUnit, ClassroomPatch


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
        person: Person = Person()
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
        self.duration = Duration(HourTimeUnit(1))
        self.attendees = []

    def build(self) -> Classroom:
        if self.position < len(self.attendees):
            self.position = len(self.attendees)
        classroom = Classroom.create(self.name, self.start_date, self.position, self.stop_date, self.duration)
        if self.attendees:
            classroom.all_attendees(self.attendees)
        return classroom

    def with_position(self, position: int) -> ClassroomBuilderForTest:
        self.position = position
        return self

    def with_attendee(self, client_id: UUID) -> ClassroomBuilderForTest:
        self.attendees.append(Attendee(client_id))
        return self

    def starting_at(self, start_at: datetime) -> ClassroomBuilderForTest:
        self.start_date = start_at
        return self

    def ending_at(self, ends_at: datetime) -> ClassroomBuilderForTest:
        self.stop_date = ends_at
        return self


class ClassroomContextBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        self.repository = None
        self.classroom_builders_for_test = []

    def build(self):
        if not self.classroom_builders_for_test:
            self.classroom_builders_for_test.append(ClassroomBuilderForTest())
        classrooms: List[Classroom] = list(map(lambda builder: builder.build(), self.classroom_builders_for_test))
        if self.repository:
            for classroom in classrooms:
                self.repository.persist(classroom)
        return self.repository, classrooms

    def persist(self, repository: Repository = None) -> ClassroomContextBuilderForTest:
        self.repository = repository if repository else MemoryClassroomRepository()
        return self

    def with_classroom(self, classroom_builder: ClassroomBuilderForTest) -> ClassroomContextBuilderForTest:
        self.classroom_builders_for_test.append(classroom_builder)
        return self

    def with_classrooms(self, *classroom_builders: ClassroomBuilderForTest) -> ClassroomContextBuilderForTest:
        for builder in classroom_builders:
            self.classroom_builders_for_test.append(builder)
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
            classroom["attendees"] = list(map(lambda attendee: {"client_id": attendee.hex}, self.attendees))
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

    def with_attendee(self, client_id: UUID) -> ClassroomPatchJsonBuilderForTest:
        self.attendees.append({"client_id": client_id.hex})
        return self
