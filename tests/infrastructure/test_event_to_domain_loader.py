from datetime import datetime, timedelta
from uuid import UUID

import pytz
from immobilus import immobilus

from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.domain.attending.session import Session, ConfirmedSession
from crm_pilates.domain.scheduling.attendee import Attendance
from crm_pilates.domain.scheduling.classroom_type import ClassroomSubject
from crm_pilates.domain.scheduling.duration import Duration, MinuteTimeUnit
from crm_pilates.domain.client.client import Client
from crm_pilates.infrastructure.event_to_domain_loader import EventToDomainLoader
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import (
    EventBuilderForTest,
    ClassroomBuilderForTest,
    ConfirmedSessionBuilderForTest,
    ClientBuilderForTest,
)


def test_load_classroom(persisted_event_store):
    events = EventBuilderForTest().classroom().build()
    expected_uuid = events[0].payload["id"]
    start_date = events[0].payload["schedule"]["start"]
    stop_date = events[0].payload["schedule"]["stop"]

    EventToDomainLoader().load()

    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(
        expected_uuid
    )
    assert classroom
    assert classroom.schedule.start == start_date
    assert classroom.schedule.stop == stop_date


def test_should_load_clients_with_credits(persisted_event_store):
    events = (
        EventBuilderForTest()
        .client(
            ClientBuilderForTest()
            .with_credit(2, ClassroomSubject.MAT)
            .with_credit(5, ClassroomSubject.MACHINE_TRIO)
            .build()
        )
        .build()
    )
    first_client_id: UUID = events[0].root_id

    EventToDomainLoader().load()

    client = RepositoryProvider.read_repositories.client.get_by_id(first_client_id)
    assert client.credits[0].value == 2
    assert client.credits[0].subject == ClassroomSubject.MAT
    assert client.credits[1].value == 5
    assert client.credits[1].subject == ClassroomSubject.MACHINE_TRIO


def test_should_load_added_credits_to_client(persisted_event_store):
    client = ClientBuilderForTest().with_credit(2, ClassroomSubject.MAT).build()
    EventBuilderForTest().client(client).nb_client(2).added_credits_for_machine_duo(
        client, 10
    ).build()

    EventToDomainLoader().load()

    client = RepositoryProvider.read_repositories.client.get_by_id(client.id)
    assert len(client.credits) == 1
    assert client.credits[0].value == 10
    assert client.credits[0].subject == ClassroomSubject.MACHINE_DUO


def test_load_clients_and_classroom_with_attendees(persisted_event_store):
    events = EventBuilderForTest().nb_client(3).classroom_with_attendees(2).build()
    first_client_id: UUID = events[0].root_id
    second_client_id: UUID = events[1].root_id
    third_client_id: UUID = events[2].root_id
    classroom_id: UUID = events[3].root_id

    EventToDomainLoader().load()

    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(
        classroom_id
    )
    assert classroom
    assert len(classroom.attendees) == 2
    assert classroom.attendees[0].id == first_client_id
    assert classroom.attendees[1].id == second_client_id
    assert RepositoryProvider.read_repositories.client.get_by_id(first_client_id)
    assert RepositoryProvider.read_repositories.client.get_by_id(second_client_id)
    assert RepositoryProvider.read_repositories.client.get_by_id(third_client_id)


def test_load_classroom_with_50_minutes_duration(persisted_event_store):
    events = (
        EventBuilderForTest()
        .classroom(
            ClassroomBuilderForTest()
            .with_duration(Duration(MinuteTimeUnit(50)))
            .build()
        )
        .build()
    )
    expected_uuid = events[0].payload["id"]

    EventToDomainLoader().load()

    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(
        expected_uuid
    )
    assert classroom
    assert classroom.duration.time_unit.value == 50
    assert isinstance(classroom.duration.time_unit, MinuteTimeUnit)


def test_load_confirmed_session(persisted_event_store):
    events = (
        EventBuilderForTest()
        .confirmed_session(
            ConfirmedSessionBuilderForTest()
            .starting_at(datetime(2021, 9, 14, 10))
            .build()
        )
        .build()
    )
    payload = events[0].payload
    session_id = payload["id"]

    EventToDomainLoader().load()

    confirmed_session: Session = RepositoryProvider.read_repositories.session.get_by_id(
        session_id
    )
    assert confirmed_session.classroom_id == payload["classroom_id"]
    assert confirmed_session.name == payload["name"]
    assert confirmed_session.position == payload["position"]
    assert confirmed_session.start == payload["schedule"]["start"]
    assert confirmed_session.stop == datetime(
        2021, 9, 14, 10, tzinfo=pytz.utc
    ) + timedelta(hours=1)
    assert len(confirmed_session.attendees) == 0


def test_should_load_events_by_date_ascending(persisted_event_store):
    with immobilus("2020-10-09 10:05:00"):
        clients_events = EventBuilderForTest().nb_client(3).build()
        clients = list(map(lambda event: event.payload["id"], clients_events))
        classroom_builder = EventBuilderForTest().classroom(
            ClassroomBuilderForTest()
            .starting_at(datetime.now())
            .with_attendees([clients[0], clients[1]])
            .build()
        )
        classroom_builder.build()
    classroom: Classroom = classroom_builder.classrooms[0]
    date = datetime(2020, 10, 16, 10, 5, tzinfo=pytz.utc)
    confirmed_session_builder = EventBuilderForTest().confirmed_session(
        ConfirmedSession.create(classroom, date)
    )
    with immobilus("2020-10-15 10:01:00"):
        EventBuilderForTest().cancel_attendee(
            confirmed_session_builder.sessions[0].id,
            [confirmed_session_builder.sessions[0].attendees[0].id],
        ).build()
    with immobilus("2020-10-15 10:00:00"):
        events = confirmed_session_builder.build()

    EventToDomainLoader().load()

    confirmed_session: Session = RepositoryProvider.read_repositories.session.get_by_id(
        events[0].payload["id"]
    )
    assert confirmed_session


def test_load_confirmed_session_with_attendees(persisted_event_store):
    events = (
        EventBuilderForTest()
        .nb_client(3)
        .classroom_with_attendees(2)
        .confirmed_session()
        .build()
    )
    payload = events[-1].payload
    session_id = payload["id"]

    EventToDomainLoader().load()

    confirmed_session: Session = RepositoryProvider.read_repositories.session.get_by_id(
        session_id
    )
    assert confirmed_session
    assert len(confirmed_session.attendees) == 2


def test_load_attendees_added_to_classroom(persisted_event_store):
    events = (
        EventBuilderForTest()
        .nb_client(3)
        .classroom(ClassroomBuilderForTest().build())
        .attendees_added(2)
        .build()
    )
    payload = events[3].payload
    classroom_id = payload["id"]

    EventToDomainLoader().load()

    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(
        classroom_id
    )
    assert classroom
    assert len(classroom.attendees) == 2


def test_load_checkin_session(persisted_event_store):
    events = (
        EventBuilderForTest()
        .nb_client(3)
        .classroom(ClassroomBuilderForTest().build())
        .attendees_added(2)
        .confirmed_session()
        .checked_in(2)
        .build()
    )
    payload = events[6].payload
    session_id = payload["session_id"]

    EventToDomainLoader().load()

    confirmed_session: Session = RepositoryProvider.read_repositories.session.get_by_id(
        session_id
    )
    assert confirmed_session
    assert len(confirmed_session.attendees) == 2
    assert confirmed_session.attendees[0].attendance == Attendance.CHECKED_IN
    assert confirmed_session.attendees[1].attendance == Attendance.CHECKED_IN


def test_load_checkout_session(persisted_event_store):
    checked_in_builder = (
        EventBuilderForTest()
        .nb_client(3)
        .classroom(ClassroomBuilderForTest().build())
        .attendees_added(2)
        .confirmed_session()
    )
    checked_in_builder.checked_in_attendees(
        [checked_in_builder.sessions[0].attendees[1].id]
    )
    events = checked_in_builder.checked_out(
        checked_in_builder.sessions[0].id,
        [checked_in_builder.sessions[0].attendees[1].id],
    ).build()
    payload = events[7].payload
    session_id = payload["session_id"]

    EventToDomainLoader().load()

    confirmed_session: Session = RepositoryProvider.read_repositories.session.get_by_id(
        session_id
    )
    assert confirmed_session
    assert len(confirmed_session.attendees) == 2
    assert confirmed_session.attendees[0].attendance == Attendance.REGISTERED
    assert confirmed_session.attendees[1].attendance == Attendance.REGISTERED


def test_should_load_session_with_cancelled_attendee_removed(persisted_event_store):
    confirmed_session_builder = (
        EventBuilderForTest()
        .nb_client(3)
        .classroom(ClassroomBuilderForTest().build())
        .attendees_added(2)
        .confirmed_session()
    )
    confirmed_session_builder.build()
    events = (
        EventBuilderForTest()
        .cancel_attendee(
            confirmed_session_builder.sessions[0].id,
            [confirmed_session_builder.sessions[0].attendees[1].id],
        )
        .build()
    )
    payload = events[0].payload
    session_id = payload["session_id"]

    EventToDomainLoader().load()

    confirmed_session: Session = RepositoryProvider.read_repositories.session.get_by_id(
        session_id
    )
    assert confirmed_session
    assert len(confirmed_session.attendees) == 1
    assert confirmed_session.attendees[0].attendance == Attendance.REGISTERED


def test_should_load_session_with_already_performed_cancelled_attendee_removal(
    persisted_event_store,
):
    confirmed_session_builder = (
        EventBuilderForTest()
        .nb_client(3)
        .classroom(ClassroomBuilderForTest().build())
        .attendees_added(2)
        .confirmed_session()
    )
    confirmed_session_builder.build()
    EventBuilderForTest().cancel_attendee(
        confirmed_session_builder.sessions[0].id,
        [confirmed_session_builder.sessions[0].attendees[1].id],
    ).build()
    events = (
        EventBuilderForTest()
        .cancel_attendee(
            confirmed_session_builder.sessions[0].id,
            [confirmed_session_builder.sessions[0].attendees[1].id],
        )
        .build()
    )
    payload = events[0].payload
    session_id = payload["session_id"]

    EventToDomainLoader().load()

    confirmed_session: Session = RepositoryProvider.read_repositories.session.get_by_id(
        session_id
    )
    assert confirmed_session
    assert len(confirmed_session.attendees) == 1
    assert confirmed_session.attendees[0].attendance == Attendance.REGISTERED


def test_missing_mapper_should_not_stop_execution(persisted_event_store):
    EventBuilderForTest().nb_client(3).classroom(
        ClassroomBuilderForTest().build()
    ).unknown_event().attendees_added(2).confirmed_session().build()

    EventToDomainLoader().load()

    clients: [Client] = RepositoryProvider.read_repositories.client.get_all()
    assert len(next(clients)) == 3
    classroom_generator: [
        Classroom
    ] = RepositoryProvider.read_repositories.classroom.get_all()
    classrooms = next(classroom_generator)
    assert len(classrooms) == 1
    assert len(classrooms[0].attendees) == 2
    sessions_generator: [
        Session
    ] = RepositoryProvider.read_repositories.session.get_all()
    sessions = next(sessions_generator)
    assert len(sessions) == 1
    assert len(sessions[0].attendees) == 2
