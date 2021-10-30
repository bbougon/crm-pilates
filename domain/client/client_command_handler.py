from typing import Tuple
from uuid import UUID

from command.command_handler import CommandHandler, Status
from domain.client.client import Client
from domain.commands import ClientCreationCommand
from event.event_store import Event, EventSourced
from infrastructure.repository_provider import RepositoryProvider


@EventSourced
class ClientCreated(Event):

    def __init__(self, root_id: UUID, firstname: str, lastname: str) -> None:
        self.firstname = firstname
        self.lastname = lastname
        super().__init__(root_id)

    def _to_payload(self):
        return {
            "id": self.root_id,
            "firstname": self.firstname,
            "lastname": self.lastname
        }


class ClientCreationCommandHandler(CommandHandler):
    def execute(self, command: ClientCreationCommand) -> Tuple[ClientCreated, Status]:
        client = Client.create(command.firstname, command.lastname)
        RepositoryProvider.write_repositories.client.persist(client)
        return ClientCreated(client._id, client.firstname, client.lastname), Status.CREATED
