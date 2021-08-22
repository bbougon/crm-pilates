from typing import List

from domain.classroom.classroom import Classroom
from web.presentation.domain.units import Units


class Duration:

    def __init__(self, duration: int, time_unit: str) -> None:
        super().__init__()
        self.duration = duration
        self.time_unit = time_unit


class DetailedClassroom:

    def __init__(self, classroom: Classroom, attendees: List[dict]) -> None:
        super().__init__()
        self.id = classroom.id
        self.name = classroom.name
        self.position = classroom.position
        self.start = classroom.schedule.start.isoformat()
        self.stop = classroom.schedule.stop.isoformat() if classroom.schedule.stop else None
        self.duration = Duration(classroom.duration.time_unit.value, Units.units()[classroom.duration.time_unit.__class__.__name__])
        self.attendees = attendees
