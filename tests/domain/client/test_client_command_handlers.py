from datetime import datetime

import pytz
from immobilus import immobilus

from crm_pilates.domain.client.client_command_handlers import (
    ClientCreated,
    ClientCreationCommandHandler,
    AddCreditsToClientCommandHandler,
    DecreaseClientCreditsCommandHandler,
    DeleteClientCommandHandler,
)
from crm_pilates.domain.commands import (
    ClientCreationCommand,
    ClientCredits,
    AddCreditsToClientCommand,
    DecreaseClientCreditsCommand,
    DeleteClientCommand,
)
from crm_pilates.domain.scheduling.attendee import Attendee
from crm_pilates.domain.scheduling.classroom_type import ClassroomSubject
from crm_pilates.domain.services import CipherServiceProvider
from crm_pilates.event.event_store import StoreLocator
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from tests.asserters.event_asserter import EventAsserter
from tests.builders.builders_for_test import (
    ClientContextBuilderForTest,
    ClientBuilderForTest,
    ClassroomContextBuilderForTest,
    ClassroomBuilderForTest,
    ConfirmedSessionContextBuilderForTest,
)
from tests.domain.services.test_services import MyDummyEncryptionService


@immobilus("2020-04-03 10:24:15.230")
def test_classroom_creation_event_is_stored(memory_event_store):
    CipherServiceProvider.service = MyDummyEncryptionService()
    result: ClientCreated = ClientCreationCommandHandler().execute(
        ClientCreationCommand(firstname="John", lastname="Doe")
    )

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClientCreated"
    assert events[0].timestamp == datetime(
        2020, 4, 3, 10, 24, 15, 230000, tzinfo=pytz.utc
    )
    EventAsserter.assert_client_created(
        events[0].payload, result.root_id, "John", "Doe"
    )


@immobilus("2020-04-03 10:24:15.230")
def test_classroom_creation_event_is_stored_with_credits(memory_event_store):
    CipherServiceProvider.service = MyDummyEncryptionService()
    result: ClientCreated = ClientCreationCommandHandler().execute(
        ClientCreationCommand(
            firstname="John",
            lastname="Doe",
            credits=[ClientCredits(2, ClassroomSubject.MAT)],
        )
    )

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClientCreated"
    assert events[0].timestamp == datetime(
        2020, 4, 3, 10, 24, 15, 230000, tzinfo=pytz.utc
    )
    EventAsserter.assert_client_created(
        events[0].payload,
        result.root_id,
        "John",
        "Doe",
        [{"value": 2, "subject": "MAT"}],
    )


def test_should_store_credits_to_client_added(memory_event_store, memory_repositories):
    client = ClientBuilderForTest().build()
    ClientContextBuilderForTest().with_client(client).persist(
        RepositoryProvider.write_repositories.client
    ).build()

    AddCreditsToClientCommandHandler().execute(
        AddCreditsToClientCommand(
            client.id,
            [
                ClientCredits(5, ClassroomSubject.MAT),
                ClientCredits(10, ClassroomSubject.MACHINE_DUO),
            ],
        )
    )

    events = StoreLocator.store.get_all()
    assert events[0].type == "ClientCreditsUpdated"
    EventAsserter.assert_client_credits_updated(
        events[0].payload,
        client.id,
        [
            {"value": 5, "subject": ClassroomSubject.MAT.value},
            {"value": 10, "subject": ClassroomSubject.MACHINE_DUO.value},
        ],
    )


@immobilus("2020-05-03 10:00:00.000")
def test_should_decrease_credits_event_with_unprovided_credits(
    memory_event_store, memory_repositories
):
    client = ClientBuilderForTest().build()
    ClientContextBuilderForTest().with_client(client).persist(
        RepositoryProvider.write_repositories.client
    ).build()
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(
            ClassroomBuilderForTest().machine_private().with_attendee(client.id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    session_repository, session = (
        ConfirmedSessionContextBuilderForTest()
        .for_classroom(classrooms[0])
        .persist(RepositoryProvider.write_repositories.session)
        .build()
    )

    DecreaseClientCreditsCommandHandler().execute(
        DecreaseClientCreditsCommand(session.id, Attendee.create(client.id))
    )

    assert client.credits[0].value == -1


@immobilus("2020-05-03 10:00:00.000")
def test_should_decrease_credits_on_expected_subject_credits(
    memory_event_store, memory_repositories
):
    client = (
        ClientBuilderForTest()
        .with_credit(5, ClassroomSubject.MACHINE_DUO)
        .with_credit(4, ClassroomSubject.MAT)
        .build()
    )
    ClientContextBuilderForTest().with_client(client).persist(
        RepositoryProvider.write_repositories.client
    ).build()
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(ClassroomBuilderForTest().mat().with_attendee(client.id))
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    session_repository, session = (
        ConfirmedSessionContextBuilderForTest()
        .for_classroom(classrooms[0])
        .persist(RepositoryProvider.write_repositories.session)
        .build()
    )

    DecreaseClientCreditsCommandHandler().execute(
        DecreaseClientCreditsCommand(session.id, Attendee.create(client.id))
    )

    assert client.credits[0].value == 5
    assert client.credits[1].value == 3


def test_should_delete_client(memory_event_store, memory_repositories):
    repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(2)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )

    DeleteClientCommandHandler().execute(DeleteClientCommand(clients[1].id))

    assert len(next(repository.get_all())) == 1
