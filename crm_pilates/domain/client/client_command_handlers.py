from typing import Tuple, List
from uuid import UUID

from crm_pilates.command.command_handler import CommandHandler, Status
from crm_pilates.domain.attending.session import Session
from crm_pilates.domain.client.client import Client, Credits
from crm_pilates.domain.commands import (
    ClientCreationCommand,
    AddCreditsToClientCommand,
    DecreaseClientCreditsCommand,
    RefundClientCreditsCommand,
)
from crm_pilates.event.event_store import Event, EventSourced
from crm_pilates.infrastructure.repository_provider import RepositoryProvider


@EventSourced
class ClientCreated(Event):
    def __init__(
        self,
        root_id: UUID,
        firstname: str,
        lastname: str,
        credits: List[Credits] = None,
    ) -> None:
        self.firstname = firstname
        self.lastname = lastname
        self.credits: List[Credits] = credits
        super().__init__(root_id)

    def _to_payload(self):
        payload = {
            "id": self.root_id,
            "firstname": self.firstname,
            "lastname": self.lastname,
        }
        if self.credits:
            payload["credits"] = list(
                map(
                    lambda credit: {
                        "value": credit.value,
                        "subject": credit.subject.value,
                    },
                    self.credits,
                )
            )
        return payload


class ClientCreationCommandHandler(CommandHandler):
    def execute(self, command: ClientCreationCommand) -> ClientCreated:
        client = Client.create(command.firstname, command.lastname, command.credits)
        RepositoryProvider.write_repositories.client.persist(client)
        return ClientCreated(
            client._id, client.firstname, client.lastname, client.credits
        )


@EventSourced
class ClientCreditsUpdated(Event):
    def __init__(self, root_id: UUID, credits: List[Credits]) -> None:
        self.credits = credits
        super().__init__(root_id)

    def _to_payload(self):
        return {
            "id": self.root_id,
            "credits": list(
                map(
                    lambda credit: {
                        "value": credit.value,
                        "subject": credit.subject.value,
                    },
                    self.credits,
                )
            ),
        }


class AddCreditsToClientCommandHandler(CommandHandler):
    def execute(
        self, command: AddCreditsToClientCommand
    ) -> Tuple[ClientCreditsUpdated, Status]:
        client: Client = RepositoryProvider.write_repositories.client.get_by_id(
            command.id
        )
        client.add_credits(command.credits)
        return ClientCreditsUpdated(client.id, client.credits), Status.UPDATED


class DecreaseClientCreditsCommandHandler(CommandHandler):
    def execute(
        self, command: DecreaseClientCreditsCommand
    ) -> Tuple[ClientCreditsUpdated, Status]:
        client: Client = RepositoryProvider.write_repositories.client.get_by_id(
            command.attendee.id
        )
        session: Session = RepositoryProvider.write_repositories.session.get_by_id(
            command.session_id
        )
        client.decrease_credits_for(session.subject)
        return ClientCreditsUpdated(client.id, client.credits), Status.UPDATED


class RefundClientCreditsCommandHandler(CommandHandler):
    def execute(
        self, command: RefundClientCreditsCommand
    ) -> Tuple[ClientCreditsUpdated, Status]:
        client: Client = RepositoryProvider.write_repositories.client.get_by_id(
            command.attendee.id
        )
        session: Session = RepositoryProvider.write_repositories.session.get_by_id(
            command.session_id
        )
        client.refund_credits_for(session.subject)
        return ClientCreditsUpdated(client.id, client.credits), Status.UPDATED
