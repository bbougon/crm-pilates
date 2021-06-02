from datetime import datetime
import uuid
from pydantic.types import UUID4


class Classroom():

    name:str
    hour:str
    day:datetime

    def __init__(self):
        self.id = uuid.uuid4()


    @staticmethod
    def create(name:str, hour:str, date: datetime):
        classroom = Classroom()
        classroom.name = name
        classroom.hour = datetime.strptime(hour, '%H:%M').time()
        classroom.day = date
        return classroom