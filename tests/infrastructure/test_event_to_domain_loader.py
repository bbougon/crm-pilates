import pytest

from datetime import datetime
from uuid import UUID

from domain.classroom.classroom import Classroom, Session
from domain.classroom.duration import Duration, MinuteTimeUnit
from infrastructure.event_to_domain_loader import EventToDomainLoader
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import EventBuilderForTest, ClassroomBuilderForTest, \
    ConfirmedSessionBuilderForTest


def test_load_classroom(database):
    events = EventBuilderForTest().classroom().persist(database).build()
    expected_uuid = events[0].payload["id"]
    start_date = events[0].payload["schedule"]["start"]
    stop_date = events[0].payload["schedule"]["stop"]

    EventToDomainLoader().load()

    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(expected_uuid)
    assert classroom
    assert classroom.schedule.start == start_date
    assert classroom.schedule.stop == stop_date


def test_load_clients_and_classroom_with_attendees(database):
    events = EventBuilderForTest().client(3).classroom_with_attendees(2).persist(database).build()
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


def test_load_classroom_with_50_minutes_duration(database):
    events = EventBuilderForTest().classroom(ClassroomBuilderForTest().with_duration(Duration(MinuteTimeUnit(50))).build()).persist(database).build()
    expected_uuid = events[0].payload["id"]

    EventToDomainLoader().load()

    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(expected_uuid)
    assert classroom
    assert classroom.duration.time_unit.value == 50
    assert isinstance(classroom.duration.time_unit, MinuteTimeUnit)


@pytest.mark.skip(reason="FIX loader in CI first thanks to ansible")
def test_load_confirmed_session(database):
    events = EventBuilderForTest().confirmed_session(ConfirmedSessionBuilderForTest().starting_at(datetime(2021, 9, 14, 10)).build()).persist(database).build()
    session_id = events[0].payload["id"]

    EventToDomainLoader().load()

    confirmed_session: Session = RepositoryProvider.read_repositories.session.get_by_id(session_id)
    assert confirmed_session