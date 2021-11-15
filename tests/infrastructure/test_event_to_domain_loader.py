from datetime import datetime, timedelta
from uuid import UUID

import pytz

from domain.classroom.classroom import Classroom, Session, Attendance
from domain.classroom.duration import Duration, MinuteTimeUnit
from infrastructure.event_to_domain_loader import EventToDomainLoader
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import EventBuilderForTest, ClassroomBuilderForTest, \
    ConfirmedSessionBuilderForTest


def test_load_classroom(persisted_event_store):
    events = EventBuilderForTest().classroom().build()
    expected_uuid = events[0].payload["id"]
    start_date = events[0].payload["schedule"]["start"]
    stop_date = events[0].payload["schedule"]["stop"]

    EventToDomainLoader().load()

    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(expected_uuid)
    assert classroom
    assert classroom.schedule.start == start_date
    assert classroom.schedule.stop == stop_date


def test_load_clients_and_classroom_with_attendees(persisted_event_store):
    events = EventBuilderForTest().client(3).classroom_with_attendees(2).build()
    first_client_id: UUID = events[0].root_id
    second_client_id: UUID = events[1].root_id
    third_client_id: UUID = events[2].root_id
    classroom_id: UUID = events[3].root_id

    EventToDomainLoader().load()

    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(classroom_id)
    assert classroom
    assert len(classroom.attendees) == 2
    assert classroom.attendees[0].id == first_client_id
    assert classroom.attendees[1].id == second_client_id
    assert RepositoryProvider.read_repositories.client.get_by_id(first_client_id)
    assert RepositoryProvider.read_repositories.client.get_by_id(second_client_id)
    assert RepositoryProvider.read_repositories.client.get_by_id(third_client_id)


def test_load_classroom_with_50_minutes_duration(persisted_event_store):
    events = EventBuilderForTest().classroom(ClassroomBuilderForTest().with_duration(Duration(MinuteTimeUnit(50))).build()).build()
    expected_uuid = events[0].payload["id"]

    EventToDomainLoader().load()

    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(expected_uuid)
    assert classroom
    assert classroom.duration.time_unit.value == 50
    assert isinstance(classroom.duration.time_unit, MinuteTimeUnit)


def test_load_confirmed_session(persisted_event_store):
    events = EventBuilderForTest().confirmed_session(ConfirmedSessionBuilderForTest().starting_at(datetime(2021, 9, 14, 10)).build()).build()
    payload = events[0].payload
    session_id = payload["id"]

    EventToDomainLoader().load()

    confirmed_session: Session = RepositoryProvider.read_repositories.session.get_by_id(session_id)
    assert confirmed_session.classroom_id == payload["classroom_id"]
    assert confirmed_session.name == payload["name"]
    assert confirmed_session.position == payload["position"]
    assert confirmed_session.start == payload["schedule"]["start"]
    assert confirmed_session.stop == datetime(2021, 9, 14, 10, tzinfo=pytz.utc) + timedelta(hours=1)
    assert len(confirmed_session.attendees) == 0


def test_load_confirmed_session_with_attendees(persisted_event_store):
    events = EventBuilderForTest().client(3).classroom_with_attendees(2).confirmed_session().build()
    payload = events[-1].payload
    session_id = payload["id"]

    EventToDomainLoader().load()

    confirmed_session: Session = RepositoryProvider.read_repositories.session.get_by_id(session_id)
    assert confirmed_session
    assert len(confirmed_session.attendees) == 2


def test_load_attendees_added_to_classroom(persisted_event_store):
    events = EventBuilderForTest().client(3).classroom(ClassroomBuilderForTest().build()).attendees_added(2).build()
    payload = events[3].payload
    classroom_id = payload["id"]

    EventToDomainLoader().load()

    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(classroom_id)
    assert classroom
    assert len(classroom.attendees) == 2


def test_load_checkin_session(persisted_event_store):
    events = EventBuilderForTest().client(3).classroom(ClassroomBuilderForTest().build()).attendees_added(2).confirmed_session().checked_in(2).build()
    payload = events[6].payload
    session_id = payload["session_id"]

    EventToDomainLoader().load()

    confirmed_session: Session = RepositoryProvider.read_repositories.session.get_by_id(session_id)
    assert confirmed_session
    assert len(confirmed_session.attendees) == 2
    assert confirmed_session.attendees[0].attendance == Attendance.CHECKED_IN
    assert confirmed_session.attendees[1].attendance == Attendance.CHECKED_IN


def test_load_checkout_session(persisted_event_store):
    checked_in_builder = EventBuilderForTest().client(3).classroom(ClassroomBuilderForTest().build()).attendees_added(
        2).confirmed_session().checked_in(1)
    checked_in_builder.build()
    events = EventBuilderForTest().checked_out(checked_in_builder.sessions[0].id, [checked_in_builder.sessions[0].attendees[1].id]).build()
    payload = events[0].payload
    session_id = payload["session_id"]

    EventToDomainLoader().load()

    confirmed_session: Session = RepositoryProvider.read_repositories.session.get_by_id(session_id)
    assert confirmed_session
    assert len(confirmed_session.attendees) == 2
    assert confirmed_session.attendees[0].attendance == Attendance.REGISTERED
    assert confirmed_session.attendees[1].attendance == Attendance.REGISTERED
