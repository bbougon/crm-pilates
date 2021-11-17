from domains.client.client import Client
from domains.repository import Repository


class ClientRepository(Repository):
    def _get_entity_type(self) -> str:
        return Client.__name__
