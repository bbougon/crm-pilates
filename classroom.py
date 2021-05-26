
import uuid
from pydantic.types import UUID4


class Classroom():

    name:str
    hour:str

    def __init__(self):
        self.id = uuid.uuid4()


    @staticmethod
    def create(name:str, hour:str):
        classroom = Classroom()
        classroom.name = name
        classroom.hour = hour
        return classroom