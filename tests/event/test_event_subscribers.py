import uuid

from immobilus import immobilus

from crm_pilates.domain.client.client_command_handlers import (
    ClientDeleted,
    ClientCreditsDecreased,
)
from crm_pilates.domain.email_notifier import MessageNotifier, Message
from crm_pilates.domain.scheduling.classroom_type import ClassroomSubject
from crm_pilates.event.event_subscribers import (
    ClientDeletedEventSubscriber,
    ClientCreditDecreasedEventSubscriber,
)
from crm_pilates.infrastructure.command_bus_provider import CommandBusProvider
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import (
    ClassroomBuilderForTest,
    ClientBuilderForTest,
)
from tests.builders.providers_for_test import CommandBusProviderForTest


def test_should_remove_attendees_from_classroom_on_client_deletion():
    attendee = uuid.uuid4()
    classroom = ClassroomBuilderForTest().with_attendee(attendee).build()
    RepositoryProvider.write_repositories.classroom.persist(classroom)
    CommandBusProviderForTest().provide()

    ClientDeletedEventSubscriber(CommandBusProvider.command_bus).consume(
        ClientDeleted(attendee)
    )

    assert len(classroom.attendees) == 0


class DummyEmailNotifier(MessageNotifier):
    def __init__(self):
        self.email_information: Message = None
        self.email_notified = False

    def send(self, message):
        self.email_notified = True
        self.email_information = message


@immobilus("2023-09-10")
def test_should_send_an_email_to_notify_the_client_he_reaches_low_credit():
    client = ClientBuilderForTest().with_mat_credit(1).build()
    RepositoryProvider.write_repositories.client.persist(client)
    email_notifier = DummyEmailNotifier()

    ClientCreditDecreasedEventSubscriber(email_notifier).consume(
        ClientCreditsDecreased(client.id, client.credits, ClassroomSubject.MAT)
    )

    assert email_notifier.email_notified is True
    assert email_notifier.email_information == {
        "to": "bertrand.bougon@gmail.com",
        "body": {
            "template": "low_credits_notification",
            "parameters": {"date": "2023-09-10", "subject": "MAT", "credits_left": 1},
        },
    }


@immobilus("2023-09-13")
def test_should_send_an_email_with_corresponding_credits():
    client = (
        ClientBuilderForTest().with_machine_duo_credit(2).with_mat_credit(1).build()
    )
    RepositoryProvider.write_repositories.client.persist(client)
    email_notifier = DummyEmailNotifier()

    ClientCreditDecreasedEventSubscriber(email_notifier).consume(
        ClientCreditsDecreased(client.id, client.credits, ClassroomSubject.MAT)
    )

    assert email_notifier.email_notified is True
    assert email_notifier.email_information == {
        "to": "bertrand.bougon@gmail.com",
        "body": {
            "template": "low_credits_notification",
            "parameters": {"date": "2023-09-13", "subject": "MAT", "credits_left": 1},
        },
    }


def test_should_not_send_an_email_if_low_credits_not_reached():
    client = (
        ClientBuilderForTest().with_machine_duo_credit(2).with_mat_credit(2).build()
    )
    RepositoryProvider.write_repositories.client.persist(client)
    email_notifier = DummyEmailNotifier()

    ClientCreditDecreasedEventSubscriber(email_notifier).consume(
        ClientCreditsDecreased(client.id, client.credits, ClassroomSubject.MAT)
    )

    assert email_notifier.email_notified is False
