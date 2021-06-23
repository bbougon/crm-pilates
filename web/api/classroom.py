from uuid import UUID

from fastapi import status, APIRouter, Response, Depends

from domain.classroom import Classroom, Duration, TimeUnit
from infrastructure.repositories import Repositories
from infrastructure.tests.memory_classroom_repository import MemoryClassroomRepository
from web.schema.classroom_creation import ClassroomCreation

router = APIRouter()

repo = Repositories({"classroom": MemoryClassroomRepository()})


def repository_provider():
    return repo


@router.post("/classrooms",
             status_code=status.HTTP_201_CREATED,
             responses={
                 201: {
                     "description": "Create a classroom"
                 }
             }
             )
def create_classroom(classroom_creation: ClassroomCreation, response: Response,
                     repositories: Repositories = Depends(repository_provider)):
    classroom = Classroom.create(
        classroom_creation.name, classroom_creation.start_date,
        Duration(classroom_creation.duration.duration, TimeUnit(classroom_creation.duration.unit.value)))
    response.headers["location"] = f"/classrooms/{classroom.id}"
    repositories.classroom.persist(classroom)
    return {"name": classroom.name, "id": classroom.id, "start_date": classroom.start_date,
            "duration": {"duration": classroom.duration.duration, "unit": classroom.duration.time_unit.value}}


@router.get("/classrooms/{id}")
def get_classroom(id: UUID, repositories: Repositories = Depends(repository_provider)):
    return repositories.classroom.get_by_id(id)
