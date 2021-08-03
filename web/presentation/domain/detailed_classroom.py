from typing import List

from domain.classroom.classroom import Classroom


class DetailedClassroom:
    class Duration:

        def __init__(self, duration: int, time_unit: str) -> None:
            super().__init__()
            self.duration = duration
            self.time_unit = time_unit

    def __init__(self, classroom: Classroom, attendees: List[dict]) -> None:
        super().__init__()
        self.id = classroom.id
        self.name = classroom.name
        self.position = classroom.position
        self.start = classroom.schedule.start.isoformat()
        self.stop = classroom.schedule.stop.isoformat() if classroom.schedule.stop else None
        self.duration = self.Duration(classroom.duration.duration, classroom.duration.time_unit.value)
        self.attendees = attendees
