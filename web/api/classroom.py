from http import HTTPStatus
from typing import Tuple
from uuid import UUID

from fastapi import status, APIRouter, Response, Depends, HTTPException

from command.command_handler import Status
from domains.classes.classroom.classroom_creation_command_handler import ClassroomCreated
from domains.classes.commands import ClassroomCreationCommand, ClassroomPatchCommand
from domains.exceptions import DomainException, AggregateNotFoundException
from infrastructure.command_bus_provider import CommandBusProvider
from web.presentation.domain.detailed_classroom import DetailedClassroom
from web.presentation.service.classroom_service import get_detailed_classroom
from web.schema.classroom_response import ClassroomReadResponse, ClassroomCreatedResponse
from web.schema.classroom_schemas import ClassroomCreation, ClassroomPatch

router = APIRouter()


@router.post("/classrooms",
             response_model=ClassroomCreatedResponse,
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
                                           list(map(lambda client: client.id, classroom_creation.attendees)))
        from command.response import Response
        result: Tuple[Response, Status] = command_bus_provider.command_bus.send(command)
        event: ClassroomCreated = result[0].event
        response.headers["location"] = f"/classrooms/{event.root_id}"
        return {
            "name": event.name,
            "id": event.root_id,
            "position": event.position,
            "schedule": {
                "start": event.schedule.start,
                "stop": event.schedule.stop
            },
            "duration": ClassroomReadResponse.to_duration(event.duration),
            "attendees": list(map(lambda attendee: {"id": attendee["id"]}, event.attendees))
        }
    except AggregateNotFoundException as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f"One of the attendees with id '{e.unknown_id}' has not been found")
    except DomainException as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=e.message)


@router.get("/classrooms/{id}",
            response_model=ClassroomReadResponse,
            responses={
                404: {
                    "description": "Classroom has not been found"
                }
            }
            )
def get_classroom(id: UUID):
    try:
        detailed_classroom: DetailedClassroom = get_detailed_classroom(id)
        return {
            "name": detailed_classroom.name,
            "id": detailed_classroom.id,
            "position": detailed_classroom.position,
            "schedule": {
                "start": detailed_classroom.start,
                "stop": detailed_classroom.stop
            },
            "duration": {
                "duration": detailed_classroom.duration.duration,
                "time_unit": detailed_classroom.duration.time_unit
            },
            "attendees": detailed_classroom.attendees
        }
    except AggregateNotFoundException:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Classroom with id '{str(id)}' not found")


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
            ClassroomPatchCommand(id, list(map(lambda client: client.id, classroom_patch.attendees))))
    except AggregateNotFoundException as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f"One of the attendees with id '{e.unknown_id}' has not been found")
    except DomainException as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=e.message)
