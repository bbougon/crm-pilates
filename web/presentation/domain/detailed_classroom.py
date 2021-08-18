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
        self.id = classroom._id
        self.name = classroom._name
        self.position = classroom._position
        self.start = classroom._schedule.start.isoformat()
        self.stop = classroom._schedule.stop.isoformat() if classroom._schedule.stop else None
        self.duration = self.Duration(classroom._duration.duration, classroom._duration.time_unit.value)
        self.attendees = attendees
