import uuid
from datetime import date, time


class Classroom():

    name:str
    schedule:str
    start_date:date

    def __init__(self):
        self.id = uuid.uuid4()


    @staticmethod
    def create(name:str, schedule:time, start_date: date):
        classroom = Classroom()
        classroom.name = name
        classroom.schedule = schedule
        classroom.start_date = start_date
        return classroom