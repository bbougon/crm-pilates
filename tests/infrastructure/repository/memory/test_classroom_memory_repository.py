from datetime import datetime
from typing import List

import pytz
from immobilus import immobilus

from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.infrastructure.repository.memory.memory_classroom_repositories import (
    MemoryClassroomRepository,
    MemoryClassRoomReadRepository,
)
from tests.builders.builders_for_test import (
    ClassroomContextBuilderForTest,
    ClassroomBuilderForTest,
)


@immobilus("2020-06-19 09:30:15.230")
def test_get_classrooms_scheduled_at():
    write_repository = MemoryClassroomRepository()
    classroom_repository = MemoryClassRoomReadRepository(write_repository)
    ClassroomContextBuilderForTest().with_classrooms(
        ClassroomBuilderForTest()
        .starting_at(datetime(2020, 6, 19, 10))
        .ending_at(datetime(2020, 7, 19, 11)),
        ClassroomBuilderForTest()
        .starting_at(datetime(2020, 6, 19, 11, 15))
        .ending_at(datetime(2020, 6, 19, 12, 15)),
        ClassroomBuilderForTest().starting_at(datetime(2020, 6, 19, 8, 45)),
    ).persist(write_repository).build()

    classrooms: List[Classroom] = next(
        classroom_repository.get_next_classrooms_from(datetime.now(tz=pytz.utc))
    )

    assert len(classrooms) == 2
    assert classrooms[0].schedule.start == datetime(2020, 6, 19, 10, tzinfo=pytz.utc)
    assert classrooms[0].schedule.stop == datetime(2020, 7, 19, 11, tzinfo=pytz.utc)
    assert classrooms[1].schedule.start == datetime(
        2020, 6, 19, 11, 15, tzinfo=pytz.utc
    )
    assert classrooms[1].schedule.stop == datetime(2020, 6, 19, 12, 15, tzinfo=pytz.utc)
