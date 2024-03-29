from typing import List, Union
from uuid import UUID

from fastapi import status, APIRouter, Response, Depends

from crm_pilates.domain.client.client import Client
from crm_pilates.domain.client.client_command_handlers import ClientCreated
from crm_pilates.domain.commands import (
    ClientCreationCommand,
    ClientCredits,
    AddCreditsToClientCommand,
    DeleteClientCommand,
)
from crm_pilates.infrastructure.command_bus_provider import CommandBusProvider
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from crm_pilates.web.api.authentication import authentication_service
from crm_pilates.web.schema.client_response import ClientReadResponse
from crm_pilates.web.schema.client_schemas import ClientCreation, Credits

router = APIRouter(dependencies=[Depends(authentication_service)])


@router.post(
    "/clients",
    status_code=status.HTTP_201_CREATED,
    tags=["clients"],
    response_model=ClientReadResponse,
    responses={
        201: {
            "description": "Create a client",
            "headers": {
                "location": {
                    "description": "The absolute path URL location of the newly created client",
                    "schema": {"type": "URL"},
                }
            },
        }
    },
)
def create_client(
    client_creation: ClientCreation,
    response: Response,
    command_bus_provider: CommandBusProvider = Depends(CommandBusProvider),
):
    from crm_pilates.command.response import Response

    result: Response = command_bus_provider.command_bus.send(
        ClientCreationCommand(
            client_creation.firstname,
            client_creation.lastname,
            __to_client_credits(client_creation.credits),
        )
    )
    event: ClientCreated = result.event
    response.headers["location"] = f"/clients/{event.root_id}"
    return __map_client(event)


@router.delete(
    "/clients/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["clients"],
    responses={
        204: {"description": "Client has been deleted"},
        404: {"description": "Client not found"},
    },
)
def delete_client(
    id: UUID, command_bus_provider: CommandBusProvider = Depends(CommandBusProvider)
):
    command_bus_provider.command_bus.send(DeleteClientCommand(id))
    return


@router.get(
    "/clients/{id}",
    status_code=status.HTTP_200_OK,
    tags=["clients"],
    response_model=ClientReadResponse,
    responses={
        200: {"description": "Client with its attributes"},
        404: {"description": "Client not found"},
    },
)
def get_client(id: UUID):
    return __map_client(RepositoryProvider.write_repositories.client.get_by_id(id))


@router.get(
    "/clients",
    status_code=status.HTTP_200_OK,
    tags=["clients"],
    response_model=List[ClientReadResponse],
    responses={200: {"description": "Get all clients"}},
)
def get_clients():
    clients = sorted(
        sorted(
            next(RepositoryProvider.read_repositories.client.get_all()),
            key=lambda client: client.firstname.lower(),
        ),
        key=lambda client: client.lastname.lower(),
    )
    return list(map(lambda client: __map_client(client), clients))


@router.post(
    "/clients/{id}/credits",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["clients"],
    description="""Update client:
                          - Add credits to client""",
    responses={204: {"description": "The request has been processed successfully."}},
)
def add_credits_to_client(
    id: UUID,
    _credits: List[Credits],
    command_bus_provider: CommandBusProvider = Depends(CommandBusProvider),
):
    command_bus_provider.command_bus.send(
        AddCreditsToClientCommand(id, __to_client_credits(_credits))
    )


def __to_client_credits(creation_credits):
    client_credits = (
        list(
            map(
                lambda credit: ClientCredits(credit.value, credit.subject),
                creation_credits,
            )
        )
        if creation_credits
        else None
    )
    return client_credits


def __map_client(client: Union[Client, ClientCreated]) -> dict:
    payload = {
        "id": client.root_id if hasattr(client, "root_id") else client.id,
        "firstname": client.firstname,
        "lastname": client.lastname,
    }
    if client.credits:
        payload["credits"] = list(
            map(
                lambda credit: {"value": credit.value, "subject": credit.subject.value},
                client.credits,
            )
        )
    return payload
