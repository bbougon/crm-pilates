from typing import Tuple, List
from uuid import UUID

from command.command_handler import CommandHandler, Status
from domain.client.client import Client, Credits
from domain.commands import ClientCreationCommand, AddCreditsToClientCommand
from event.event_store import Event, EventSourced
from infrastructure.repository_provider import RepositoryProvider


@EventSourced
class ClientCreated(Event):

    def __init__(self, root_id: UUID, firstname: str, lastname: str, credits: List[Credits] = None) -> None:
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
            payload["credits"] = list(map(lambda credit: {"value": credit.value, "type": credit.type.value}, self.credits))
        return payload


class ClientCreationCommandHandler(CommandHandler):

    def execute(self, command: ClientCreationCommand) -> Tuple[ClientCreated, Status]:
        client = Client.create(command.firstname, command.lastname, command.credits)
        RepositoryProvider.write_repositories.client.persist(client)
        return ClientCreated(client._id, client.firstname, client.lastname, client.credits), Status.CREATED


class CreditsToClientAdded(Event):
    def __init__(self, root_id: UUID, credits: List[Credits]) -> None:
        super().__init__(root_id)

    def _to_payload(self):
        pass


class AddCreditsToClientCommandHandler(CommandHandler):

    def execute(self, command: AddCreditsToClientCommand) -> Tuple[CreditsToClientAdded, Status]:
        client: Client = RepositoryProvider.write_repositories.client.get_by_id(command.id)
        client.add_credits(command.credits)
        return CreditsToClientAdded(client.id, client.credits), Status.UPDATED
