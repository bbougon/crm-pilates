from __future__ import annotations

import uuid
from abc import abstractmethod
from datetime import datetime
from typing import List

from domain.classroom.classroom import Classroom, Schedule, Attendee, ConfirmedSession
from domain.classroom.classroom_creation_command_handler import ClassroomCreated
from domain.classroom.classroom_patch_command_handler import AllAttendeesAdded
from domain.classroom.duration import Duration, HourTimeUnit, MinuteTimeUnit
from domain.classroom.session_creation_command_handler import ConfirmedSessionEvent
from domain.client.client import Client
from domain.client.client_command_handler import ClientCreated
from event.event_store import StoreLocator, Event
from infrastructure.repository_provider import RepositoryProvider


class EventToDomainMapper:

    @abstractmethod
    def map(self, event: Event) -> EventToDomainMapper:
        pass

    @abstractmethod
    def and_persist(self) -> None:
        pass


class EventToClassroomMapper(EventToDomainMapper):

    def __init__(self) -> None:
        super().__init__()
        self.classroom: Classroom = None

    def map(self, event: ClassroomCreated) -> EventToDomainMapper:
        schedule_stop = event.payload["schedule"]["stop"]
        schedule_start = event.payload["schedule"]["start"]
        schedule = Schedule(datetime.fromisoformat(schedule_start), datetime.fromisoformat(schedule_stop) if schedule_stop else None)
        duration = event.payload["duration"]
        time_unit = MinuteTimeUnit(duration["duration"]) if duration["time_unit"] else HourTimeUnit(duration["duration"])
        self.classroom = Classroom(event.payload["name"], event.payload["position"], schedule, Duration(time_unit))
        self.classroom._id = uuid.UUID(event.payload["id"])
        self.classroom._attendees = list(map(lambda attendee: Attendee(uuid.UUID(attendee["id"])), event.payload["attendees"])) if "attendees" in event.payload else []
        return self

    def and_persist(self) -> None:
        RepositoryProvider.write_repositories.classroom.persist(self.classroom)


class EventToClientMapper(EventToDomainMapper):

    def __init__(self) -> None:
        super().__init__()
        self.client: Client = None

    def map(self, event: Event) -> EventToDomainMapper:
        self.client = Client(event.payload["firstname"], event.payload["lastname"])
        self.client._id = uuid.UUID(event.payload["id"])
        return self

    def and_persist(self) -> None:
        RepositoryProvider.write_repositories.client.persist(self.client)


class EventToConfirmedSessionMapper(EventToDomainMapper):

    def map(self, event: Event) -> EventToDomainMapper:
        self.session = None
        payload = event.payload
        start = datetime.fromisoformat(payload["schedule"]["start"])
        stop = datetime.fromisoformat(payload["schedule"]["stop"])
        attendees = list(map(lambda attendee: Attendee(uuid.UUID(attendee["id"])), payload["attendees"])) if "attendees" in payload else []
        self.session = ConfirmedSession(uuid.UUID(payload["classroom_id"]), payload["name"], payload["position"], start, MinuteTimeUnit(divmod((stop - start).seconds, 60)[0]), attendees)
        self.session._id = uuid.UUID(payload["id"])
        return self

    def and_persist(self) -> None:
        RepositoryProvider.write_repositories.session.persist(self.session)


class EventToAttendeesAddedMapper(EventToDomainMapper):

    def map(self, event: Event) -> EventToDomainMapper:
        payload = event.payload
        classroom_id = event.root_id
        attendees = list(map(lambda attendee: Attendee(uuid.UUID(attendee["id"])), payload["attendees"])) if "attendees" in payload else []
        classroom: Classroom = RepositoryProvider.write_repositories.classroom.get_by_id(classroom_id)
        classroom._attendees = attendees
        return self

    def and_persist(self) -> None:
        pass


class EventToDomainLoader:
    def __init__(self) -> None:
        self.mappers = {
            ClassroomCreated.event.__name__: EventToClassroomMapper,
            ClientCreated.event.__name__: EventToClientMapper,
            ConfirmedSessionEvent.event.__name__: EventToConfirmedSessionMapper,
            AllAttendeesAdded.event.__name__: EventToAttendeesAddedMapper
        }

    def load(self) -> None:
        events: List[Event] = StoreLocator.store.get_all()
        for event in events:
            if event.type in self.mappers:
                self.mappers[event.type]().map(event).and_persist()
