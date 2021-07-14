from uuid import UUID

from fastapi import status, APIRouter, Response, Depends

from domain.classroom.classroom_command_handler import ClassroomCreated
from domain.commands import ClassroomCreationCommand
from infrastructure.command_bus_provider import CommandBusProvider
from infrastructure.repository_provider import RepositoryProvider
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
                     command_bus_provider: CommandBusProvider = Depends(CommandBusProvider)):
    command = ClassroomCreationCommand(classroom_creation.name, classroom_creation.position, classroom_creation.duration,
                                       classroom_creation.start_date, classroom_creation.stop_date, list(map(lambda client: client.client_id, classroom_creation.attendees)))
    event: ClassroomCreated = command_bus_provider.command_bus.send(command).event
    response.headers["location"] = f"/classrooms/{event.root_id}"
    return {"name": event.name, "id": event.root_id, "position": event.position, "start_date": event.schedule.start,
            "stop_date": event.schedule.stop,
            "duration": {"duration": event.duration.duration, "unit": event.duration.time_unit.value},
            "attendees": event.attendees}


@router.get("/classrooms/{id}")
def get_classroom(id: UUID, repository_provider: RepositoryProvider = Depends(RepositoryProvider)):
    return repository_provider.repositories.classroom.get_by_id(id)
