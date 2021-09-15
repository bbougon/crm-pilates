from uuid import UUID

from domain.classroom.classroom import Classroom
from domain.classroom.duration import Duration, MinuteTimeUnit
from infrastructure.event_to_domain_loader import EventToDomainLoader
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import EventBuilderForTest, ClassroomBuilderForTest


def test_load_classroom(database):
    events = EventBuilderForTest().classroom().persist(database).build()
    expected_uuid = events[0].payload["id"]
    start_date = events[0].payload["schedule"]["start"]
    stop_date = events[0].payload["schedule"]["stop"]

    EventToDomainLoader(database).load()

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

    EventToDomainLoader(database).load()

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

    EventToDomainLoader(database).load()

    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(expected_uuid)
    assert classroom
    assert classroom.duration.time_unit.value == 50
    assert isinstance(classroom.duration.time_unit, MinuteTimeUnit)
