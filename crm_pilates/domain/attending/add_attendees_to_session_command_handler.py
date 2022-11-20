from uuid import UUID

from crm_pilates.command.command_bus import CommandBus
from crm_pilates.command.response import Response
from crm_pilates.command.saga_handler import SagaHandler
from crm_pilates.domain.attending.session import ConfirmedSession
from crm_pilates.domain.commands import SessionCreationCommand
from crm_pilates.domain.exceptions import AggregateNotFoundException, DomainException
from crm_pilates.domain.sagas import AddAttendeesToSessionSaga
from crm_pilates.domain.scheduling.attendee import Attendee
from crm_pilates.event.event_store import Event, EventSourced
from crm_pilates.infrastructure.repository_provider import RepositoryProvider


@EventSourced
class AttendeesToSessionAdded(Event):
    def __init__(self, root_id: UUID, attendees: [Attendee]) -> None:
        self.attendees_added = attendees
        super().__init__(root_id)

    def _to_payload(self) -> dict:
        return {
            "session_id": self.root_id,
            "attendees": list(
                map(
                    lambda attendee: {
                        "id": attendee.id,
                        "attendance": attendee.attendance.value,
                    },
                    self.attendees_added,
                )
            ),
        }


class AddAttendeesToSessionSagaHandler(SagaHandler):
    def __init__(self, command_bus: CommandBus) -> None:
        super().__init__(command_bus)

    def execute(self, saga: AddAttendeesToSessionSaga) -> AttendeesToSessionAdded:
        try:
            for attendee in saga.attendees:
                RepositoryProvider.read_repositories.client.get_by_id(attendee)
        except AggregateNotFoundException:
            raise DomainException(f"Attendee with id {attendee} has not been found")
        session = (
            RepositoryProvider.write_repositories.session.get_by_classroom_id_and_date(
                saga.classroom_id, saga.session_date
            )
        )
        if session:
            session_id = session.id
        else:
            created_session: Response = self._command_bus.send(
                SessionCreationCommand(saga.classroom_id, saga.session_date)
            )
            session_id = created_session.event.root_id

        session: ConfirmedSession = (
            RepositoryProvider.write_repositories.session.get_by_id(session_id)
        )
        attendees = list(
            map(lambda attendee: Attendee.create(attendee), saga.attendees)
        )
        session.add_attendees(attendees)
        return AttendeesToSessionAdded(session.id, attendees)
