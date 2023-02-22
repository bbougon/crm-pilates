import uuid

from crm_pilates.domain.client.client_command_handlers import ClientDeleted
from crm_pilates.event.event_subscribers import ClientDeletedEventSubscriber
from crm_pilates.infrastructure.command_bus_provider import CommandBusProvider
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import ClassroomBuilderForTest
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
