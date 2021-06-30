from uuid import UUID

from fastapi import status, APIRouter, Response, Depends

from command.command_bus import CommandBus
from domain.classroom.commands import ClassroomCreationCommand
from infrastructure.repositories import Repositories
from infrastructure.tests.memory_classroom_repository import MemoryClassroomRepository
from web.schema.classroom_creation import ClassroomCreation

router = APIRouter()

repo = Repositories({"classroom": MemoryClassroomRepository()})


def repository_provider():
    return repo


command_bus = CommandBus(repo)


def command_bus_provider():
    return command_bus

@router.post("/classrooms",
             status_code=status.HTTP_201_CREATED,
             responses={
                 201: {
                     "description": "Create a classroom"
                 }
             }
             )
def create_classroom(classroom_creation: ClassroomCreation, response: Response,
                     command_bus_impl:CommandBus = Depends(command_bus_provider)):
    command = ClassroomCreationCommand(classroom_creation.name, classroom_creation.duration,
                                       classroom_creation.start_date)
    response__ = command_bus_impl.send(command)
    response.headers["location"] = f"/classrooms/{response__.id}"
    return {"name": response__.name, "id": response__.id, "start_date": response__.start_date,
            "duration": {"duration": response__.duration.duration, "unit": response__.duration.time_unit.value}}


@router.get("/classrooms/{id}")
def get_classroom(id: UUID, repositories: Repositories = Depends(repository_provider)):
    return repositories.classroom.get_by_id(id)
