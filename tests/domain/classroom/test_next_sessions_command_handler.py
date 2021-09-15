from datetime import datetime

from immobilus import immobilus

from domain.classroom.next_sessions_command_handler import NextSessionsCommandHandler, NextScheduledSessions
from domain.commands import GetNextSessionsCommand
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import ClassroomBuilderForTest, ClientContextBuilderForTest, \
    ClassroomContextBuilderForTest, SessionContextBuilderForTest


@immobilus("2021-08-22T14:50")
def test_has_no_next_sessions():
    next_sessions: NextScheduledSessions = NextSessionsCommandHandler().execute(GetNextSessionsCommand(datetime.now()))

    assert next_sessions.sessions == []


@immobilus("2021-08-23T08:50")
def test_next_sessions_with_confirmed_sessions(memory_repositories):
    client_repository, clients = ClientContextBuilderForTest().with_one_client().persist(RepositoryProvider.write_repositories.client).build()
    classroom_repository, classrooms = ClassroomContextBuilderForTest()\
        .with_classroom(ClassroomBuilderForTest().starting_at(datetime(2021, 8, 23, 10)).ending_at(datetime(2022, 7, 14, 11)).with_attendee(clients[0].id))\
        .with_classroom(ClassroomBuilderForTest().starting_at(datetime(2021, 8, 23, 11, 15)).ending_at(datetime(2022, 7, 14, 12, 15)).with_attendee(clients[0].id))\
        .persist(RepositoryProvider.write_repositories.classroom).build()
    repository, confirmed_session = SessionContextBuilderForTest().confirm().with_classroom(classrooms[0]).at(datetime(2021, 8, 23, 10)).persist(RepositoryProvider.write_repositories.session).build()

    next_sessions: NextScheduledSessions = NextSessionsCommandHandler().execute(GetNextSessionsCommand(datetime.now()))

    assert next_sessions.sessions[0].root_id == confirmed_session.id


@immobilus("2021-10-14T08:50")
def test_next_sessions_with_classroom_and_no_next_session(memory_repositories):
    ClassroomContextBuilderForTest() \
        .with_classroom(ClassroomBuilderForTest().starting_at(datetime(2021, 10, 13, 10)).ending_at(datetime(2022, 7, 14, 11))) \
        .persist(RepositoryProvider.write_repositories.classroom).build()

    next_sessions: NextScheduledSessions = NextSessionsCommandHandler().execute(GetNextSessionsCommand(datetime.now()))

    assert len(next_sessions.sessions) == 0
