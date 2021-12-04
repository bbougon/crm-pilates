from typing import Tuple, List, Union
from uuid import UUID

from fastapi import status, APIRouter, Response, Depends, HTTPException

from command.command_handler import Status
from domain.client.client import Client
from domain.client.client_command_handler import ClientCreated
from domain.commands import ClientCreationCommand, ClientCredits
from domain.exceptions import AggregateNotFoundException
from infrastructure.command_bus_provider import CommandBusProvider
from infrastructure.repository_provider import RepositoryProvider
from web.schema.client_creation import ClientCreation
from web.schema.client_response import ClientReadResponse

router = APIRouter()


@router.post("/clients",
             status_code=status.HTTP_201_CREATED,
             response_model=ClientReadResponse,
             responses={
                 201: {
                     "description": "Create a client",
                     "headers": {
                         "location": {
                             "description": "The absolute path URL location of the newly created client",
                             "schema": {"type": "URL"},
                         }
                     }
                 }
             }
             )
def create_client(client_creation: ClientCreation, response: Response,
                  command_bus_provider: CommandBusProvider = Depends(CommandBusProvider)):
    from command.response import Response
    client_credits = list(map(lambda credit: ClientCredits(credit.value, credit.type), client_creation.credits)) if client_creation.credits else None
    result: Tuple[Response, Status] = command_bus_provider.command_bus.send(
        ClientCreationCommand(client_creation.firstname, client_creation.lastname, client_credits))
    event: ClientCreated = result[0].event
    response.headers["location"] = f"/clients/{event.root_id}"
    return __map_client(event)


@router.get("/clients/{id}",
            status_code=status.HTTP_200_OK,
            response_model=ClientReadResponse,
            responses={
                200: {
                    "description": "Client with its attributes"
                },
                404: {
                    "description": "Client not found"
                }
            }
            )
def get_client(id: UUID):
    try:
        client: Client = RepositoryProvider.write_repositories.client.get_by_id(id)
        return __map_client(client)
    except AggregateNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Client with id '{e.unknown_id}' not found")


@router.get("/clients",
            status_code=status.HTTP_200_OK,
            response_model=List[ClientReadResponse],
            responses={
                200: {
                    "description": "Get all clients"
                }
            })
def get_clients():
    clients = RepositoryProvider.read_repositories.client.get_all()
    return list(map(lambda client: __map_client(client), next(clients)))


def __map_client(client: Union[Client, ClientCreated] ) -> dict:
    payload = {"id": client.root_id if hasattr(client, "root_id") else client.id, "firstname": client.firstname, "lastname": client.lastname}
    if client.credits:
        payload["credits"] = list(map(lambda credit: {"value": credit.value, "type": credit.type.value}, client.credits))
    return payload
