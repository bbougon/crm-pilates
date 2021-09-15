from __future__ import annotations

import uuid
from abc import abstractmethod
from datetime import datetime
from typing import List

from domain.classroom.classroom import Classroom, Schedule, Attendee
from domain.classroom.classroom_creation_command_handler import ClassroomCreated
from domain.classroom.duration import Duration, HourTimeUnit, MinuteTimeUnit
from domain.client.client import Client
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


class EventToDomainLoader:
    def __init__(self, database) -> None:
        self.database = database
        self.mappers = {
            "ClassroomCreated": EventToClassroomMapper,
            "ClientCreated": EventToClientMapper
        }

    def load(self) -> None:
        events: List[Event] = StoreLocator.store.get_all()
        for event in events:
            if event.type in self.mappers:
                self.mappers[event.type]().map(event).and_persist()
