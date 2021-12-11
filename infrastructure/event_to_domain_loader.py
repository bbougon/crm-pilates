from __future__ import annotations

import uuid
from abc import abstractmethod
from typing import List

import arrow

from domain.classroom.classroom import Classroom, Schedule, ConfirmedSession, Session
from domain.classroom.attendee import Attendee, Attendance
from domain.classroom.classroom_creation_command_handler import ClassroomCreated
from domain.classroom.classroom_patch_command_handler import AllAttendeesAdded
from domain.classroom.classroom_type import ClassroomSubject
from domain.classroom.duration import Duration, HourTimeUnit, MinuteTimeUnit
from domain.classroom.session.attendee_session_cancellation_saga_handler import AttendeeSessionCancelled
from domain.classroom.session.session_checkin_saga_handler import SessionCheckedIn
from domain.classroom.session.session_checkout_command_handler import SessionCheckedOut
from domain.classroom.session.session_creation_command_handler import ConfirmedSessionEvent
from domain.client.client import Client, Credits
from domain.client.client_command_handlers import ClientCreated, ClientCreditsUpdated
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
        schedule = Schedule(arrow.get(schedule_start).datetime, arrow.get(schedule_stop).datetime if schedule_stop else None)
        duration = event.payload["duration"]
        time_unit = MinuteTimeUnit(duration["duration"]) if duration["time_unit"] else HourTimeUnit(duration["duration"])
        self.classroom = Classroom(event.payload["name"], event.payload["position"], schedule, ClassroomSubject[event.payload["subject"]], Duration(time_unit))
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
        if "credits" in event.payload:
            self.client.credits = list(map(lambda credit: Credits(credit["value"], ClassroomSubject[credit["subject"]]), event.payload["credits"]))
        return self

    def and_persist(self) -> None:
        RepositoryProvider.write_repositories.client.persist(self.client)


class EventToConfirmedSessionMapper(EventToDomainMapper):

    def map(self, event: Event) -> EventToDomainMapper:
        self.session = None
        payload = event.payload
        start = arrow.get(payload["schedule"]["start"]).datetime
        stop = arrow.get(payload["schedule"]["stop"]).datetime
        attendees = list(map(lambda attendee: Attendee(uuid.UUID(attendee["id"])), payload["attendees"])) if "attendees" in payload else []
        self.session = ConfirmedSession(uuid.UUID(payload["classroom_id"]), payload["name"], payload["position"], ClassroomSubject[payload["subject"]], start, MinuteTimeUnit(divmod((stop - start).seconds, 60)[0]), attendees)
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


class EventToSessionCheckedInMapper(EventToDomainMapper):
    def map(self, event: Event) -> EventToDomainMapper:
        payload = event.payload
        attendee_id = uuid.UUID(payload["attendee"]["id"])
        session: Session = RepositoryProvider.write_repositories.session.get_by_id(event.root_id)
        for _attendee in session.attendees:
            if _attendee.id == attendee_id:
                _attendee.attendance = Attendance[payload["attendee"]["attendance"]]
        return self

    def and_persist(self) -> None:
        pass


class EventToSessionCheckedOutMapper(EventToSessionCheckedInMapper):
    pass


class EventToAttendeeSessionCancelledMapper(EventToDomainMapper):

    def map(self, event: Event) -> EventToDomainMapper:
        payload = event.payload
        attendee_id = uuid.UUID(payload["attendee"]["id"])
        session: Session = RepositoryProvider.write_repositories.session.get_by_id(event.root_id)
        filtered_attendee: Attendee = next(filter(lambda attendee: attendee.id == attendee_id, session.attendees), None)
        if filtered_attendee:
            session.attendees.remove(Attendee.create(attendee_id))
        return self

    def and_persist(self) -> None:
        pass


class CreditsToClientAddedMapper(EventToDomainMapper):

    def map(self, event: ClientCreditsUpdated) -> EventToDomainMapper:
        payload = event.payload
        client_id = uuid.UUID(payload["id"])
        client: Client = RepositoryProvider.write_repositories.client.get_by_id(client_id)
        credits: List[Credits] = list(map(lambda credit: Credits(credit["value"], ClassroomSubject[credit["subject"]]), payload["credits"]))
        client.credits = credits
        return self

    def and_persist(self) -> None:
        pass


class EventToDomainLoader:
    def __init__(self) -> None:
        self.mappers = {
            ClassroomCreated.event.__name__: EventToClassroomMapper,
            ClientCreated.event.__name__: EventToClientMapper,
            ConfirmedSessionEvent.event.__name__: EventToConfirmedSessionMapper,
            AllAttendeesAdded.event.__name__: EventToAttendeesAddedMapper,
            SessionCheckedIn.event.__name__: EventToSessionCheckedInMapper,
            SessionCheckedOut.event.__name__: EventToSessionCheckedOutMapper,
            AttendeeSessionCancelled.event.__name__: EventToAttendeeSessionCancelledMapper,
            ClientCreditsUpdated.event.__name__: CreditsToClientAddedMapper
        }

    def load(self) -> None:
        events: List[Event] = StoreLocator.store.get_all()
        for event in events:
            if event.type in self.mappers:
                self.mappers[event.type]().map(event).and_persist()
