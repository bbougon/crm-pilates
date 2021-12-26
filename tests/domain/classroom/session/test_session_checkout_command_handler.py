from datetime import datetime

import pytz

from command.command_handler import Status
from domain.classroom.session.session_checkin_saga_handler import SessionCheckinSagaHandler, SessionCheckedIn
from domain.classroom.session.session_checkout_command_handler import SessionCheckoutCommandHandler
from domain.commands import SessionCheckoutCommand
from domain.sagas import SessionCheckinSaga
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import ClientContextBuilderForTest, ClientBuilderForTest, \
    ClassroomContextBuilderForTest, ClassroomBuilderForTest
from tests.builders.providers_for_test import CommandBusProviderForTest


def test_should_refund_client_credits_on_checkout_after_checkin(memory_event_store):
    client_repository, clients = ClientContextBuilderForTest() \
        .with_clients(1) \
        .with_client(ClientBuilderForTest().with_mat_credit(10).build()) \
        .persist(RepositoryProvider.write_repositories.client) \
        .build()
    client = clients[1]
    repository, classrooms = ClassroomContextBuilderForTest() \
        .with_classroom(ClassroomBuilderForTest().starting_at(datetime(2020, 8, 3, 11, 0)).with_attendee(clients[0].id).with_attendee(client.id)) \
        .persist(RepositoryProvider.write_repositories.classroom) \
        .build()
    classroom = classrooms[0]
    result: [SessionCheckedIn, Status] = SessionCheckinSagaHandler(CommandBusProviderForTest().provide().command_bus).execute(
        SessionCheckinSaga(classroom.id, datetime(2020, 8, 3, 11, 0, tzinfo=pytz.utc), client.id))

    SessionCheckoutCommandHandler().execute(SessionCheckoutCommand(result[0].root_id, client.id))

    assert client.credits[0].value == 10
