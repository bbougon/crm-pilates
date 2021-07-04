from uuid import UUID

from fastapi import status, APIRouter, Response, Depends

from command.command_bus import CommandBus
from domain.commands import ClassroomCreationCommand
from infrastructure.repositories import Repositories
from infrastructure.providers import repository_provider, command_bus_provider
from web.schema.classroom_creation import ClassroomCreation

router = APIRouter()


@router.post("/classrooms",
             status_code=status.HTTP_201_CREATED,
             responses={
                 201: {
                     "description": "Create a classroom"
                 }
             }
             )
def create_classroom(classroom_creation: ClassroomCreation, response: Response,
                     command_bus_impl: CommandBus = Depends(command_bus_provider)):
    command = ClassroomCreationCommand(classroom_creation.name, classroom_creation.position, classroom_creation.duration,
                                       classroom_creation.start_date, classroom_creation.stop_date)
    event = command_bus_impl.send(command).event
    response.headers["location"] = f"/classrooms/{event.id}"
    return {"name": event.name, "id": event.id, "position": event.position, "start_date": event.schedule.start,
            "stop_date": event.schedule.stop,
            "duration": {"duration": event.duration.duration, "unit": event.duration.time_unit.value}}


@router.get("/classrooms/{id}")
def get_classroom(id: UUID, repositories: Repositories = Depends(repository_provider)):
    return repositories.classroom.get_by_id(id)
