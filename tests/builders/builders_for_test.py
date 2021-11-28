from __future__ import annotations

import itertools
import uuid
from abc import abstractmethod
from datetime import datetime
from typing import List
from uuid import UUID

import pytz
from mimesis import Person, Text, Numeric, Datetime

from domain.classroom.classroom import Classroom, ScheduledSession, ConfirmedSession
from domain.classroom.attendee import Attendee
from domain.classroom.classroom_creation_command_handler import ClassroomCreated
from domain.classroom.classroom_patch_command_handler import AllAttendeesAdded
from domain.classroom.classroom_repository import ClassroomRepository
from domain.classroom.duration import Duration, HourTimeUnit
from domain.classroom.session.attendee_session_cancellation_saga_handler import AttendeeSessionCancelled
from domain.classroom.session.session_checkin_saga_handler import SessionCheckedIn
from domain.classroom.session.session_checkout_command_handler import SessionCheckedOut
from domain.classroom.session.session_creation_command_handler import ConfirmedSessionEvent
from domain.client.client import Client
from domain.client.client_command_handler import ClientCreated
from domain.repository import Repository
from event.event_store import Event, EventSourced
from infrastructure.repository.memory.memory_classroom_repositories import MemoryClassroomRepository
from infrastructure.repository.memory.memory_client_repositories import MemoryClientRepository
from infrastructure.repository_provider import RepositoryProvider
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
        self.position: int = Numeric().integer_number(1, 6)
        self.start_date: datetime = Datetime().datetime().astimezone(pytz.utc)
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

    def with_attendees(self, attendees: [UUID]) -> ClassroomBuilderForTest:
        self.attendees.extend(list(map(lambda uuid: Attendee(uuid), attendees)))
        return self

    def starting_at(self, start_at: datetime) -> ClassroomBuilderForTest:
        self.start_date = datetime(start_at.year, start_at.month, start_at.day, start_at.hour, start_at.minute,
                                   start_at.second, tzinfo=start_at.tzinfo or pytz.utc)
        return self

    def ending_at(self, ends_at: datetime) -> ClassroomBuilderForTest:
        self.stop_date = datetime(ends_at.year, ends_at.month, ends_at.day, ends_at.hour, ends_at.minute,
                                  ends_at.second, tzinfo=ends_at.tzinfo or pytz.utc)
        return self

    def with_duration(self, duration: Duration) -> ClassroomBuilderForTest:
        self.duration = duration
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
        self.position: int = Numeric().integer_number(1, 6)
        self.start_date: datetime = Datetime().datetime()
        self.stop_date: datetime = None
        self.attendees: List[UUID] = []
        self.duration: dict = None

    def build(self):
        classroom = {"name": self.classroom_name, "position": self.position, "start_date": self.start_date.isoformat()}
        if self.attendees:
            classroom["attendees"] = list(map(lambda attendee: {"id": attendee.hex}, self.attendees))
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


class SessionContextBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        self.classroom = ClassroomBuilderForTest().build()
        self.repository: ClassroomRepository = None
        self.date: datetime = self.classroom.schedule.start.replace(tzinfo=pytz.utc)
        self.client_checkin: UUID = None
        self.session_to_create = "confirm_session_at"
        self.cancelled_attendee: UUID = None

    def build(self):
        session: ConfirmedSession = getattr(self.classroom, self.session_to_create)(self.date)
        if self.client_checkin:
            session.checkin(Attendee.create(self.client_checkin))
        if self.cancelled_attendee:
            session.cancel(Attendee.create(self.cancelled_attendee))
        if self.repository:
            self.repository.persist(session)
        return self.repository, session

    def with_classroom(self, classroom: Classroom) -> SessionContextBuilderForTest:
        self.classroom = classroom
        return self

    def at(self, date: datetime) -> SessionContextBuilderForTest:
        self.date = date.replace(tzinfo=date.tzinfo or pytz.utc)
        return self

    def persist(self, repository: ClassroomRepository = None) -> SessionContextBuilderForTest:
        self.repository = repository if repository else MemoryClassroomRepository()
        return self

    def checkin(self, client_id: UUID) -> SessionContextBuilderForTest:
        self.client_checkin = client_id
        return self

    def confirm(self) -> SessionContextBuilderForTest:
        self.session_to_create = "confirm_session_at"
        return self

    def cancel(self, client_id: UUID):
        self.cancelled_attendee = client_id
        return self


class ClassroomPatchJsonBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        self.attendees = []

    def build(self):
        return ClassroomPatch.parse_obj({"attendees": self.attendees})

    def with_attendee(self, client_id: UUID) -> ClassroomPatchJsonBuilderForTest:
        self.attendees.append({"id": client_id.hex})
        return self


class SessionCheckinJsonBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        self.attendee: UUID = None
        self.session_date: datetime = None
        repository, classrooms = ClassroomContextBuilderForTest().persist(
            RepositoryProvider.write_repositories.classroom).build()
        self.classroom: Classroom = classrooms[0]
        self.classroom_id = self.classroom.id

    def build(self):
        if not self.attendee:
            repository, clients = ClientContextBuilderForTest().persist(
                RepositoryProvider.write_repositories.client).build()
            self.attendee = clients[0].id
            self.classroom.all_attendees([Attendee.create(self.attendee)])
        if not self.session_date:
            self.session_date = self.classroom.schedule.start
        return {"classroom_id": str(self.classroom_id), "session_date": self.session_date.isoformat(),
                "attendee": str(self.attendee)}

    def for_classroom(self, classroom: Classroom) -> SessionCheckinJsonBuilderForTest:
        self.classroom_id = classroom.id
        return self

    def for_session(self, session: ScheduledSession) -> SessionCheckinJsonBuilderForTest:
        self.classroom_id: UUID = session.classroom_id
        self.session_date: datetime = session.start
        return self

    def for_attendee(self, attendee_id: UUID) -> SessionCheckinJsonBuilderForTest:
        self.attendee = attendee_id
        return self

    def at(self, date: datetime) -> SessionCheckinJsonBuilderForTest:
        self.session_date = date.replace(tzinfo=date.tzinfo or pytz.utc)
        return self

    def for_classroom_id(self, classroom_id) -> SessionCheckinJsonBuilderForTest:
        self.classroom_id = classroom_id
        return self


class AttendeeSessionCancellationJsonBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        self.session_date: datetime = None
        repository, classrooms = ClassroomContextBuilderForTest().persist(
            RepositoryProvider.write_repositories.classroom).build()
        self.classroom: Classroom = classrooms[0]
        self.classroom_id = self.classroom.id

    def build(self):
        return {
            "classroom_id": str(self.classroom_id),
            "session_date": self.session_date.isoformat()
        }

    def for_classroom(self, classroom: Classroom) -> AttendeeSessionCancellationJsonBuilderForTest:
        self.classroom_id = classroom.id
        return self

    def at(self, date: datetime) -> AttendeeSessionCancellationJsonBuilderForTest:
        self.session_date = date.replace(tzinfo=date.tzinfo or pytz.utc)
        return self


class ConfirmedSessionBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        self.classroom = ClassroomBuilderForTest().build()
        self.start_at = self.classroom.schedule.start.replace(tzinfo=pytz.utc)

    def build(self):
        return ConfirmedSession.create(self.classroom, self.start_at)

    def starting_at(self, start_at: datetime) -> ConfirmedSessionBuilderForTest:
        self.start_at = start_at.replace(tzinfo=pytz.utc)
        self.classroom = ClassroomBuilderForTest().starting_at(self.start_at).build()
        return self

    def for_classroom(self, classroom: Classroom) -> ConfirmedSessionBuilderForTest:
        self.classroom = classroom
        self.start_at = self.classroom.schedule.start.replace(tzinfo=pytz.utc)
        return self


@EventSourced
class UnknownEvent(Event):

    def __init__(self, root_id: UUID, value: str) -> None:
        self.value = value
        super().__init__(root_id)

    def _to_payload(self):
        return {"event": self.value}


class EventBuilderForTest(Builder):

    def __init__(self) -> None:
        super().__init__()
        self.events = List[Event]
        self.event_to_store = []
        self.classrooms = []
        self.clients = []
        self.sessions = []
        self.sessions = []

    def build(self):
        self.events = [self.__to_event(event, value) for event, value in self.event_to_store]
        return self.events

    def classroom(self, classroom: Classroom = None) -> EventBuilderForTest:
        classroom = classroom or ClassroomBuilderForTest().build()
        self.event_to_store.append((ClassroomCreated, (classroom.id, classroom.name, classroom.position, classroom.duration, classroom.schedule, [])))
        self.classrooms.append(classroom)
        return self

    def client(self, nb_clients: int) -> EventBuilderForTest:
        clients: List[Client] = [ClientBuilderForTest().build() for _ in range(nb_clients)]
        self.event_to_store.extend(
            [(ClientCreated, (client.id, client.firstname, client.lastname)) for client in clients])
        self.clients.extend(clients)
        return self

    def classroom_with_attendees(self, nb_attendees: int):
        attendees: [Client] = list(itertools.islice(self.clients, nb_attendees)) if self.clients else self.client(
            nb_attendees).clients
        classroom = ClassroomBuilderForTest().with_attendees(list(map(lambda client: client.id, attendees))).build()
        self.event_to_store.append((ClassroomCreated, (classroom.id, classroom.name, classroom.position, classroom.duration, classroom.schedule, attendees)))
        self.classrooms.append(classroom)
        return self

    def confirmed_session(self, confirmed_session: ConfirmedSession = None) -> EventBuilderForTest:
        def get_confirmed_session(_confirmed_session: ConfirmedSession):
            if not confirmed_session:
                classroom: Classroom = self.classrooms[0] if self.classrooms else ClassroomBuilderForTest().build()
                _confirmed_session = ConfirmedSessionBuilderForTest().for_classroom(classroom).build()
            return _confirmed_session

        confirmed_session = get_confirmed_session(confirmed_session)
        self.event_to_store.append((ConfirmedSessionEvent, (confirmed_session.id, confirmed_session.classroom_id, confirmed_session.name, confirmed_session.position, confirmed_session.start, confirmed_session.stop, confirmed_session.attendees)))
        self.sessions.append(confirmed_session)
        return self

    def attendees_added(self, nb_attendees: int) -> EventBuilderForTest:
        clients: [Client] = list(itertools.islice(self.clients, nb_attendees)) if self.clients else self.client(
            nb_attendees).clients
        attendees = list(map(lambda client: Attendee(client.id), clients))
        classroom: Classroom = self.classrooms[0]
        classroom._attendees = attendees
        self.event_to_store.append((AllAttendeesAdded, (classroom.id, attendees)))
        return self

    def checked_in(self, nb_attendees_checked_in: int) -> EventBuilderForTest:
        confirmed_session: ConfirmedSession = self.sessions[0]
        for i in range(nb_attendees_checked_in):
            attendee = confirmed_session.attendees[i - 1]
            self.event_to_store.append((SessionCheckedIn, (confirmed_session.id, confirmed_session.checkin(attendee))))
        return self

    def checked_out(self, session_id: UUID, attendees_ids: [int]) -> EventBuilderForTest:
        for id in attendees_ids:
            attendee = Attendee.create(id)
            attendee.checkout()
            self.event_to_store.append((SessionCheckedOut, (session_id, attendee)))
        return self

    def cancel_attendee(self, session_id: UUID, cancel_attendees_ids: [int]):
        for id in cancel_attendees_ids:
            attendee = Attendee.create(id)
            self.event_to_store.append((AttendeeSessionCancelled, (session_id, attendee)))
        return self

    def unknown_event(self):
        self.event_to_store.append((UnknownEvent, (uuid.uuid4(), "unknown")))
        return self

    def __to_event(self, _call, _args):
        return _call(*_args)
