import uuid
from datetime import datetime

import pytest
import pytz
from immobilus import immobilus

from crm_pilates.domain.attending.session import (
    Session,
    ConfirmedSession,
    InvalidSessionStartDateException,
    ScheduledSession,
)
from crm_pilates.domain.attending.sessions import Sessions
from crm_pilates.domain.exceptions import DomainException
from crm_pilates.domain.scheduling.attendee import Attendee
from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.domain.scheduling.duration import Duration, MinuteTimeUnit
from tests.builders.builders_for_test import (
    ClassroomBuilderForTest,
    ConfirmedSessionBuilderForTest,
)


def test_session_in_range_should_return_sessions_until_classroom_stops():
    classroom: Classroom = (
        ClassroomBuilderForTest()
        .starting_at(datetime(2020, 6, 1, 10))
        .ending_at(datetime(2020, 7, 13, 10, 45))
        .with_duration(Duration(MinuteTimeUnit(45)))
        .build()
    )

    sessions: [Session] = Sessions.sessions_in_range(
        classroom, datetime(2020, 7, 1), datetime(2020, 7, 31, 23, 59, 59)
    )

    assert len(sessions) == 2
    assert sessions[-1].start == datetime(2020, 7, 13, 10, tzinfo=pytz.utc)
    assert sessions[-1].stop == datetime(2020, 7, 13, 10, 45, tzinfo=pytz.utc)


def test_should_confirm_session_with_scheduled_time():
    classroom: Classroom = (
        ClassroomBuilderForTest()
        .starting_at(datetime(2019, 6, 7, 10))
        .with_duration(Duration(MinuteTimeUnit(45)))
        .build()
    )

    session: ConfirmedSession = ConfirmedSession.create(
        classroom, datetime(2019, 6, 7, 10).replace(tzinfo=pytz.utc)
    )

    assert session.stop == datetime(2019, 6, 7, 10, 45).replace(tzinfo=pytz.utc)


def test_should_not_confirm_session_with_invalid_date():
    with pytest.raises(InvalidSessionStartDateException) as e:
        classroom: Classroom = (
            ClassroomBuilderForTest().starting_at(datetime(2019, 6, 7, 10)).build()
        )
        ConfirmedSession.create(
            classroom, datetime(2019, 6, 8, 10).replace(tzinfo=pytz.utc)
        )

    assert (
        e.value.message
        == f"Classroom '{classroom.name}' starting at '{classroom.schedule.start.isoformat()}' cannot be set at '{datetime(2019, 6, 8, 10, tzinfo=pytz.utc).isoformat()}', closest possible dates are '{datetime(2019, 6, 7, 10, tzinfo=pytz.utc).isoformat()}' or '{datetime(2019, 6, 14, 10, tzinfo=pytz.utc).isoformat()}'"
    )


@immobilus("2020-9-24 08:24:15.230")
def test_should_retrieve_next_classroom_session():
    classroom = (
        ClassroomBuilderForTest()
        .with_name("next session")
        .with_position(2)
        .starting_at(datetime(2020, 9, 10, 10))
        .ending_at(datetime(2021, 6, 10, 11))
        .build()
    )

    session: ScheduledSession = Sessions.next_session(classroom)

    assert session
    assert session.name == "next session"
    assert session.start == datetime(2020, 9, 24, 10, tzinfo=pytz.utc)
    assert session.stop == datetime(2020, 9, 24, 11, tzinfo=pytz.utc)
    assert session.position == 2
    assert len(session.attendees) == 0


@immobilus("2020-9-24 08:24:15.230")
def test_should_retrieve_next_classroom_session_with_duration():
    classroom = (
        ClassroomBuilderForTest()
        .starting_at(datetime(2020, 9, 10, 10))
        .ending_at(datetime(2021, 6, 10, 10))
        .with_duration(Duration(MinuteTimeUnit(45)))
        .build()
    )

    session: ScheduledSession = Sessions.next_session(classroom)

    assert session.stop == datetime(2020, 9, 24, 10, 45, tzinfo=pytz.utc)


@immobilus("2020-9-23 08:24:15.230")
def test_should_not_retrieve_classroom_next_session_if_no_session_today():
    classroom = (
        ClassroomBuilderForTest()
        .starting_at(datetime(2020, 9, 10, 10))
        .ending_at(datetime(2021, 6, 10, 10))
        .build()
    )

    assert Sessions.next_session(classroom) is None


@immobilus("2021-08-22 08:24:15.230")
def test_should_retrieve_next_session_if_today_is_sunday_and_next_session_on_monday():
    classroom = (
        ClassroomBuilderForTest()
        .starting_at(datetime(2021, 8, 23, 10))
        .ending_at(datetime(2022, 7, 12, 10))
        .build()
    )

    assert Sessions.next_session(classroom)


def test_should_not_confirm_session_with_invalid_date_and_time():
    with pytest.raises(InvalidSessionStartDateException) as e:
        classroom: Classroom = (
            ClassroomBuilderForTest()
            .with_name("classroom to be confirmed")
            .starting_at(datetime(2020, 6, 1, 10))
            .build()
        )
        ConfirmedSession.create(
            classroom, datetime(2020, 6, 8, 10, 30, tzinfo=pytz.utc)
        )

    assert (
        e.value.message
        == f"Classroom 'classroom to be confirmed' starting at '{classroom.schedule.start.isoformat()}' cannot be set at '{datetime(2020, 6, 8, 10, 30, tzinfo=pytz.utc).isoformat()}', closest possible dates are '{datetime(2020, 6, 8, 10, tzinfo=pytz.utc).isoformat()}' or '{datetime(2020, 6, 15, 10, tzinfo=pytz.utc).isoformat()}'"
    )


def test_should_not_confirm_session_with_date_prior_to_classroom_start_date():
    with pytest.raises(InvalidSessionStartDateException) as e:
        classroom: Classroom = (
            ClassroomBuilderForTest().starting_at(datetime(2020, 6, 1, 10)).build()
        )
        ConfirmedSession.create(
            classroom, datetime(2020, 5, 25, 10, 0, tzinfo=pytz.utc)
        )

    assert (
        e.value.message
        == f"Classroom '{classroom.name}' starting at '{classroom.schedule.start.isoformat()}' cannot be set before"
    )


def test_checkin_unknown_attendee_should_be_handled():
    classroom: Classroom = (
        ClassroomBuilderForTest().starting_at(datetime(2019, 6, 7, 10)).build()
    )
    session: ConfirmedSession = (
        ConfirmedSessionBuilderForTest().for_classroom(classroom).build()
    )
    unknown_attendee_id = uuid.uuid4()

    with pytest.raises(DomainException) as e:
        session.checkin(Attendee.create(unknown_attendee_id))

    assert (
        e.value.message
        == f"Attendee with id {str(unknown_attendee_id)} could not be checked in"
    )


def test_checkout_unknown_attendee_should_be_handled():
    classroom: Classroom = (
        ClassroomBuilderForTest().starting_at(datetime(2019, 6, 7, 10)).build()
    )
    session: ConfirmedSession = (
        ConfirmedSessionBuilderForTest().for_classroom(classroom).build()
    )
    unknown_attendee_id = uuid.uuid4()

    with pytest.raises(DomainException) as e:
        session.checkout(Attendee.create(unknown_attendee_id))

    assert (
        e.value.message
        == f"Attendee with id {str(unknown_attendee_id)} could not be checked out"
    )


def test_should_not_add_more_attendees_than_position_available():
    classroom: Classroom = (
        ClassroomBuilderForTest()
        .with_position(2)
        .starting_at(datetime(2019, 6, 7, 10))
        .build()
    )
    session: ConfirmedSession = (
        ConfirmedSessionBuilderForTest().for_classroom(classroom).build()
    )

    with pytest.raises(DomainException) as e:
        session.add_attendees(
            [
                Attendee.create(uuid.uuid4()),
                Attendee.create(uuid.uuid4()),
                Attendee.create(uuid.uuid4()),
            ]
        )

    assert (
        e.value.message
        == "Cannot add attendees, there is 2 position(s) available, you tried to add 3 attendee(s)"
    )


def test_should_not_duplicate_attendee():
    existing_attendee = uuid.uuid4()
    classroom: Classroom = (
        ClassroomBuilderForTest()
        .with_position(2)
        .with_attendees([existing_attendee])
        .starting_at(datetime(2019, 6, 7, 10))
        .build()
    )
    session: ConfirmedSession = (
        ConfirmedSessionBuilderForTest().for_classroom(classroom).build()
    )

    session.add_attendees([(Attendee.create(existing_attendee))])

    assert len(session.attendees) == 1
