from fastapi import FastAPI, status

from classroom import Classroom
from classroom_creation import ClassroomCreation

app = FastAPI(
    title="CRM Pilates"
)


@app.get("/")
def hello_world():
    return {"message": "Hello world"}


@app.post("/classroom",
          status_code=status.HTTP_201_CREATED,
          responses={
              201: {
                  "description": "Create a classroom"
              }
          }
          )
def create_classroom(classroom_creation: ClassroomCreation):
    classroom = Classroom.create(
        classroom_creation.name, classroom_creation.hour)
    return {"name": classroom.name,
            "hour": classroom.hour, "id": classroom.id}
