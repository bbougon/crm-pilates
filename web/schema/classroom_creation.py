from datetime import date
from pydantic import BaseModel


class ClassroomCreation(BaseModel):
    name: str
    hour: str
    day: date
