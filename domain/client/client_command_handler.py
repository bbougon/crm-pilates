from uuid import UUID

from command.command_handler import CommandHandler
from domain.client.client import Client
from domain.commands import ClientCreationCommand
from event.event_store import Event, EventSourced
from infrastructure.repository_provider import RepositoryProvider


@EventSourced
class ClientCreated(Event):

    def __init__(self, root_id: UUID, firstname: str, lastname: str) -> None:
        super().__init__(root_id)
        self.firstname = firstname
        self.lastname = lastname

    def _to_payload(self):
        return {
            "id": self.root_id,
            "firstname": self.firstname,
            "lastname": self.lastname
        }


class ClientCreationCommandHandler(CommandHandler):
    def execute(self, command: ClientCreationCommand) -> Event:
        client = Client.create(command.firstname, command.lastname)
        RepositoryProvider.write_repositories.client.persist(client)
        return ClientCreated(client._id, client.firstname, client.lastname)
