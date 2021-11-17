from typing import Tuple, List
from uuid import UUID

from fastapi import status, APIRouter, Response, Depends, HTTPException

from command.command_handler import Status
from domains.classes.client.client import Client
from domains.classes.client.client_command_handler import ClientCreated
from domains.classes.commands import ClientCreationCommand
from domains.exceptions import AggregateNotFoundException
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
    result: Tuple[Response, Status] = command_bus_provider.command_bus.send(
        ClientCreationCommand(client_creation.firstname, client_creation.lastname))
    event: ClientCreated = result[0].event
    response.headers["location"] = f"/clients/{event.root_id}"
    return {"id": event.root_id, "firstname": event.firstname, "lastname": event.lastname}


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
        return {
            "id": client._id,
            "firstname": client.firstname,
            "lastname": client.lastname
        }
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
    return __map_client(next(clients))


def __map_client(clients: List[Client]) -> List[dict]:
    return [{"id": client.id, "firstname": client.firstname, "lastname": client.lastname} for client in clients]
