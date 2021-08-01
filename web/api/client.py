from uuid import UUID

from fastapi import status, APIRouter, Response, Depends, HTTPException

from domain.client.client_command_handler import ClientCreated
from domain.commands import ClientCreationCommand
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
    event: ClientCreated = command_bus_provider.command_bus.send(
        ClientCreationCommand(client_creation.firstname, client_creation.lastname)).event
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
        client = RepositoryProvider.repositories.client.get_by_id(id)
        return {
            "id": client.id,
            "firstname": client.firstname,
            "lastname": client.lastname
        }
    except AggregateNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Client with id '{e.unknown_id}' not found")