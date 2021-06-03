from datetime import date, time

from pydantic import BaseModel


class ClassroomCreation(BaseModel):
    name: str
    schedule: time
    start_date: date
