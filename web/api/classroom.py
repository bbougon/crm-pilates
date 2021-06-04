from fastapi import status, APIRouter, Response, Depends

from domain.classroom import Classroom, Duration, TimeUnit
from domain.classroom_repository import ClassroomRepository
from infrastructure.tests.memory_classroom_repository import MemoryClassroomRepository
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
def create_classroom(classroom_creation: ClassroomCreation, response: Response, repository: ClassroomRepository = Depends(MemoryClassroomRepository)):
    classroom = Classroom.create(
        classroom_creation.name, classroom_creation.schedule, classroom_creation.start_date,
        Duration(classroom_creation.duration.duration, TimeUnit(classroom_creation.duration.unit.value)))
    response.headers["location"] = f"/classrooms/{classroom.id}"
    repository.persist(classroom)
    return {"name": classroom.name,
            "schedule": classroom.schedule, "id": classroom.id, "start_date": classroom.start_date,
            "duration": {"duration": classroom.duration.duration, "unit": classroom.duration.time_unit.value}}
