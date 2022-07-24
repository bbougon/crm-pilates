from typing import List
from uuid import UUID

from crm_pilates.domain.classroom.classroom import Classroom
from crm_pilates.domain.classroom.classroom_type import ClassroomSubject
from crm_pilates.web.presentation.domain.detailed_attendee import DetailedAttendee
from crm_pilates.web.presentation.domain.units import Units


class Duration:

    def __init__(self, duration: int, time_unit: str) -> None:
        super().__init__()
        self.duration = duration
        self.time_unit = time_unit


class DetailedClassroom:

    def __init__(self, classroom: Classroom, attendees: List[DetailedAttendee]) -> None:
        super().__init__()
        self.id: UUID = classroom.id
        self.name: str = classroom.name
        self.subject: ClassroomSubject = classroom.subject
        self.position: int = classroom.position
        self.start: str = classroom.schedule.start.isoformat()
        self.stop: str = classroom.schedule.stop.isoformat() if classroom.schedule.stop else None
        self.duration: Duration = Duration(classroom.duration.time_unit.value, Units.units()[classroom.duration.time_unit.__class__.__name__])
        self.attendees: List[DetailedAttendee] = attendees
