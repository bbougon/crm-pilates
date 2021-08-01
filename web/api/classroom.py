from http import HTTPStatus
from uuid import UUID

from fastapi import status, APIRouter, Response, Depends, HTTPException

from domain.classroom.classroom import Classroom
from domain.classroom.classroom_creation_command_handler import ClassroomCreated
from domain.commands import ClassroomCreationCommand, ClassroomPatchCommand
from domain.exceptions import DomainException, AggregateNotFoundException
from infrastructure.command_bus_provider import CommandBusProvider
from infrastructure.repository_provider import RepositoryProvider
from web.schema.classroom_response import ClassroomReadResponse
from web.schema.classroom_schemas import ClassroomCreation, ClassroomPatch

router = APIRouter()


@router.post("/classrooms",
             status_code=status.HTTP_201_CREATED,
             responses={
                 201: {
                     "description": "Create a classroom",
                     "headers": {
                         "location": {
                             "description": "The absolute path URL location of the newly created classroom",
                             "schema": {"type": "URL"},
                         }
                     }
                 },
                 404: {
                     "description": "See body message details"
                 },
                 409: {
                     "description": "See body message details"
                 }
             }
             )
def create_classroom(classroom_creation: ClassroomCreation, response: Response,
                     command_bus_provider: CommandBusProvider = Depends(CommandBusProvider)):
    try:
        command = ClassroomCreationCommand(classroom_creation.name, classroom_creation.position,
                                           classroom_creation.duration,
                                           classroom_creation.start_date, classroom_creation.stop_date,
                                           list(map(lambda client: client.client_id, classroom_creation.attendees)))
        event: ClassroomCreated = command_bus_provider.command_bus.send(command).event
        response.headers["location"] = f"/classrooms/{event.root_id}"
        return {"name": event.name, "id": event.root_id, "position": event.position, "start_date": event.schedule.start,
                "stop_date": event.schedule.stop,
                "duration": {"duration": event.duration.duration, "unit": event.duration.time_unit.value},
                "attendees": event.attendees}
    except AggregateNotFoundException as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f"One of the attendees with id '{e.unknown_id}' has not been found")
    except DomainException as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=e.message)


@router.get("/classrooms/{id}",
            response_model=ClassroomReadResponse)
def get_classroom(id: UUID):
    classroom: Classroom = RepositoryProvider.repositories.classroom.get_by_id(id)
    return {
        "name": classroom.name,
        "id": classroom.id,
        "position": classroom.position,
        "schedule": {
            "start": classroom.schedule.start.isoformat(),
            "stop": classroom.schedule.stop.isoformat() if classroom.schedule.stop else None
        },
        "duration": {
            "duration": classroom.duration.duration,
            "time_unit": classroom.duration.time_unit.value
        },
        "attendees": []
    }


@router.patch("/classrooms/{id}",
              status_code=status.HTTP_204_NO_CONTENT,
              description="Add attendees to a classroom. This resource works as a patch, "
                          "you must provide all classroom attendees (i.e: you had Clara already added to the classroom,"
                          " if you want John to join, you must provide both Clara and John "
                          "otherwise Clara will be removed",
              responses={
                  404: {
                       "description": "See body message details"
                  },
                  409: {
                      "description": "See body message details"
                  }
              }
              )
def update_classroom(id: UUID, classroom_patch: ClassroomPatch,
                     command_bus_provider: CommandBusProvider = Depends(CommandBusProvider)):
    try:
        command_bus_provider.command_bus.send(
            ClassroomPatchCommand(id, list(map(lambda client: client.client_id, classroom_patch.attendees))))
    except AggregateNotFoundException as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f"One of the attendees with id '{e.unknown_id}' has not been found")
    except DomainException as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=e.message)
