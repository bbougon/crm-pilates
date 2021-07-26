from fastapi import status, APIRouter, Response, Depends

from domain.client.client_command_handler import ClientCreated
from domain.commands import ClientCreationCommand
from infrastructure.command_bus_provider import CommandBusProvider
from web.schema.client_creation import ClientCreation

router = APIRouter()


@router.post("/clients",
             status_code=status.HTTP_201_CREATED,
             responses={
                 201: {
                     "description": "Create a client"
                 }
             }
             )
def create_client(client_creation: ClientCreation, response: Response,
                  command_bus_provider: CommandBusProvider = Depends(CommandBusProvider)):
    event: ClientCreated = command_bus_provider.command_bus.send(
        ClientCreationCommand(client_creation.firstname, client_creation.lastname)).event
    response.headers["location"] = f"/clients/{event.root_id}"
    return {"id": event.root_id, "firstname": event.firstname, "lastname": event.lastname}