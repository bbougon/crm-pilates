from datetime import datetime

import pytest
import pytz

from crm_pilates.command.command_handler import Status
from crm_pilates.domain.attending.session_checkin_saga_handler import (
    SessionCheckinSagaHandler,
    SessionCheckedIn,
)
from crm_pilates.domain.attending.session_checkout_command_handler import (
    SessionCheckoutCommandHandler,
)
from crm_pilates.domain.commands import SessionCheckoutCommand
from crm_pilates.domain.exceptions import DomainException
from crm_pilates.domain.sagas import SessionCheckinSaga
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import (
    ClientContextBuilderForTest,
    ClientBuilderForTest,
    ClassroomContextBuilderForTest,
    ClassroomBuilderForTest,
)
from tests.builders.providers_for_test import CommandBusProviderForTest


def test_should_refund_client_credits_on_checkout_after_checkin(memory_event_store):
    client_repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(1)
        .with_client(ClientBuilderForTest().with_mat_credit(10).build())
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    client = clients[1]
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(
            ClassroomBuilderForTest()
            .starting_at(datetime(2020, 8, 3, 11, 0))
            .with_attendee(clients[0].id)
            .with_attendee(client.id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    classroom = classrooms[0]
    result: [SessionCheckedIn, Status] = SessionCheckinSagaHandler(
        CommandBusProviderForTest().provide().command_bus
    ).execute(
        SessionCheckinSaga(
            classroom.id, datetime(2020, 8, 3, 11, 0, tzinfo=pytz.utc), client.id
        )
    )

    SessionCheckoutCommandHandler().execute(
        SessionCheckoutCommand(result[0].root_id, client.id)
    )

    assert client.credits[0].value == 10


def test_should_not_refund_client_credits_on_two_consecutives_checkout_after_checkin(
    memory_event_store,
):
    client_repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(1)
        .with_client(ClientBuilderForTest().with_mat_credit(10).build())
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    client = clients[1]
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(
            ClassroomBuilderForTest()
            .starting_at(datetime(2020, 8, 3, 11, 0))
            .with_attendee(clients[0].id)
            .with_attendee(client.id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    classroom = classrooms[0]
    result: [SessionCheckedIn, Status] = SessionCheckinSagaHandler(
        CommandBusProviderForTest().provide().command_bus
    ).execute(
        SessionCheckinSaga(
            classroom.id, datetime(2020, 8, 3, 11, 0, tzinfo=pytz.utc), client.id
        )
    )

    with pytest.raises(DomainException) as e:
        SessionCheckoutCommandHandler().execute(
            SessionCheckoutCommand(result[0].root_id, client.id)
        )
        SessionCheckoutCommandHandler().execute(
            SessionCheckoutCommand(result[0].root_id, client.id)
        )

    assert client.credits[0].value == 10
    assert (
        e.value.message
        == "Cannot checkout as attendee is already registered (i.e not checked in)."
    )
