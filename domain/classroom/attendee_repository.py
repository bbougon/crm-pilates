from domain.classroom.attendee import Attendee
from domain.repository import Repository


class AttendeeRepository(Repository):

    def _get_entity_type(self) -> str:
        return Attendee.__name__
