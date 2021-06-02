from fastapi import status, APIRouter

from domain.classroom import Classroom
from web.schema.classroom_creation import ClassroomCreation

router = APIRouter()


@router.post("/classroom",
             status_code=status.HTTP_201_CREATED,
             responses={
                 201: {
                     "description": "Create a classroom"
                 }
             }
             )
def create_classroom(classroom_creation: ClassroomCreation):
    classroom = Classroom.create(
        classroom_creation.name, classroom_creation.hour, classroom_creation.day)
    return {"name": classroom.name,
            "hour": classroom.hour, "id": classroom.id}
