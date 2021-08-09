from typing import List

from domain.classroom.classroom import Classroom
from domain.client.client import Client


class Session:

    def __init__(self, classroom: Classroom, attendees: List[Client]) -> None:
        super().__init__()
        self.__classroom = classroom
        self.__attendees = attendees

    @property
    def attendees(self):
        return self.__attendees

    @property
    def name(self):
        return self.__classroom.name

    @property
    def id(self):
        return self.__classroom.id

    @property
    def position(self):
        return self.__classroom.position

    @property
    def duration(self):
        return self.__classroom.duration

    @property
    def start(self):
        return self.__classroom.schedule.start

    @property
    def stop(self):
        return self.__classroom.schedule.stop
