from crm_pilates.domain.client.client import Client
from crm_pilates.domain.repository import Repository


class ClientRepository(Repository):
    def _get_entity_type(self) -> str:
        return Client.__name__
