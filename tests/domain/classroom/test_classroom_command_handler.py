from datetime import datetime

from immobilus import immobilus

from domain.classroom.classroom import TimeUnit
from domain.classroom.classroom_command_handler import ClassroomCreationCommandHandler, ClassroomCreated
from domain.commands import ClassroomCreationCommand
from event.event_store import StoreLocator
from infrastructure.repositories import Repositories
from infrastructure.repository.memory.memory_classroom_repository import MemoryClassroomRepository
from tests.infrastructure.event.memory_event_store import MemoryEventStore
from web.schema.classroom_creation import Duration


@immobilus("2020-4-03 10:24:15.230")
def test_classroom_creation_event_is_stored():
    StoreLocator.store = MemoryEventStore()
    command_handler = ClassroomCreationCommandHandler(Repositories({"classroom": MemoryClassroomRepository()}))

    classroom_created: ClassroomCreated = command_handler.execute(
        ClassroomCreationCommand(name="classroom", position=2, start_date=datetime(2020, 5, 7, 11, 0),
                                 duration=Duration.parse_obj({"duration": 1, "unit": "HOUR"})))

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClassroomCreated"
    assert events[0].timestamp == datetime(2020, 4, 3, 10, 24, 15, 230000)
    assert events[0].payload == {
        "id": classroom_created.root_id,
        "name": "classroom", "position": 2,
        "duration": {
            "duration": 1,
            "time_unit": TimeUnit.HOUR
        },
        "schedule": {
            "start": datetime(2020, 5, 7, 11, 0),
            "stop": None
        }
    }
