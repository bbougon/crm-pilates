from domain.client.client import Client
from domain.repository import Repository


class ClientRepository(Repository):
    def _get_entity_type(self) -> str:
        return Client.__name__
