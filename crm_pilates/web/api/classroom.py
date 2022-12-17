from uuid import UUID

from fastapi import status, APIRouter, Response, Depends

from crm_pilates.domain.commands import ClassroomScheduleCommand, ClassroomPatchCommand
from crm_pilates.domain.scheduling.classroom_schedule_command_handler import (
    ClassroomScheduled,
)
from crm_pilates.domain.scheduling.classroom_type import ClassroomSubject
from crm_pilates.infrastructure.command_bus_provider import CommandBusProvider
from crm_pilates.web.api.authentication import authentication_service
from crm_pilates.web.presentation.domain.detailed_classroom import DetailedClassroom
from crm_pilates.web.presentation.service.classroom_service import (
    get_detailed_classroom,
)
from crm_pilates.web.schema.classroom_response import (
    ClassroomReadResponse,
    ClassroomScheduledResponse,
)
from crm_pilates.web.schema.classroom_schemas import ClassroomSchedule, ClassroomPatch

router = APIRouter(dependencies=[Depends(authentication_service)])


@router.post(
    "/classrooms",
    response_model=ClassroomScheduledResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["classroom"],
    responses={
        201: {
            "description": "Create a classroom",
            "headers": {
                "location": {
                    "description": "The absolute path URL location of the newly created classroom",
                    "schema": {"type": "URL"},
                }
            },
        },
        404: {"description": "See body message details"},
        400: {"description": "See body message details"},
    },
)
def create_classroom(
    classroom_schedule: ClassroomSchedule,
    response: Response,
    command_bus_provider: CommandBusProvider = Depends(CommandBusProvider),
):
    command = ClassroomScheduleCommand(
        classroom_schedule.name,
        classroom_schedule.position,
        classroom_schedule.duration,
        ClassroomSubject[classroom_schedule.subject],
        classroom_schedule.start_date,
        classroom_schedule.stop_date,
        list(map(lambda attendee: attendee.id, classroom_schedule.attendees)),
    )
    from crm_pilates.command.response import Response

    result: Response = command_bus_provider.command_bus.send(command)
    event: ClassroomScheduled = result.event
    response.headers["location"] = f"/classrooms/{event.root_id}"
    return {
        "name": event.name,
        "id": event.root_id,
        "position": event.position,
        "subject": event.subject.value,
        "schedule": {"start": event.schedule.start, "stop": event.schedule.stop},
        "duration": ClassroomReadResponse.to_duration(event.duration),
        "attendees": list(
            map(lambda attendee: {"id": attendee["id"]}, event.attendees)
        ),
    }


@router.get(
    "/classrooms/{id}",
    response_model=ClassroomReadResponse,
    tags=["classroom"],
    responses={404: {"description": "Classroom has not been found"}},
)
def get_classroom(id: UUID):
    detailed_classroom: DetailedClassroom = get_detailed_classroom(id)
    return {
        "name": detailed_classroom.name,
        "id": detailed_classroom.id,
        "position": detailed_classroom.position,
        "subject": detailed_classroom.subject.value,
        "schedule": {
            "start": detailed_classroom.start,
            "stop": detailed_classroom.stop,
        },
        "duration": {
            "duration": detailed_classroom.duration.duration,
            "time_unit": detailed_classroom.duration.time_unit,
        },
        "attendees": detailed_classroom.attendees,
    }


@router.patch(
    "/classrooms/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["classroom"],
    description="Add attendees to a classroom. This resource works as a patch, "
    "you must provide all classroom attendees (i.e: you had Clara already added to the classroom,"
    " if you want John to join, you must provide both Clara and John "
    "otherwise Clara will be removed",
    responses={
        404: {"description": "See body message details"},
        409: {"description": "See body message details"},
    },
)
def update_classroom(
    id: UUID,
    classroom_patch: ClassroomPatch,
    command_bus_provider: CommandBusProvider = Depends(CommandBusProvider),
):
    command_bus_provider.command_bus.send(
        ClassroomPatchCommand(
            id, list(map(lambda client: client.id, classroom_patch.attendees))
        )
    )
