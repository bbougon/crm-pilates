from datetime import datetime, timedelta
from typing import List

import arrow
import pytz

from crm_pilates.domain.attending.session import Session, ScheduledSession
from crm_pilates.domain.datetimes import Weekdays
from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.domain.scheduling.date_time_comparator import (
    DateComparator,
    DateTimeComparator,
)


class Sessions:
    @staticmethod
    def sessions_in_range(
        classroom: Classroom, start_date: datetime, end_date: datetime
    ) -> List[Session]:
        days: [datetime] = list(
            map(
                lambda day_range: day_range.date(),
                arrow.Arrow.range("day", start_date, end_date),
            )
        )
        sessions: [Session] = []
        classroom_start_date = classroom.schedule.start
        for day in days:
            if (
                DateComparator(classroom_start_date.date(), day)
                .same_day()
                .before()
                .compare()
                and DateComparator(day, end_date.date()).before().compare()
                and DateComparator(day, classroom.schedule.stop.date())
                .before()
                .compare()
            ):
                sessions.append(
                    Session(
                        classroom.id,
                        classroom.name,
                        classroom.position,
                        classroom.subject,
                        datetime(
                            day.year,
                            day.month,
                            day.day,
                            classroom_start_date.hour,
                            classroom_start_date.minute,
                            tzinfo=pytz.utc
                            if classroom_start_date.tzinfo is None
                            else classroom_start_date.tzinfo,
                        ),
                        classroom.duration.time_unit,
                        classroom.attendees,
                    )
                )
        return sessions

    @staticmethod
    def next_session(classroom: Classroom) -> ScheduledSession:
        schedule = classroom.schedule
        if Sessions.__has_session_today(schedule) or (
            Sessions.today_is_sunday() and Sessions.__next_session_on_monday()
        ):
            start: datetime = datetime.utcnow().replace(
                hour=schedule.start.hour,
                minute=schedule.start.minute,
                second=0,
                microsecond=0,
                tzinfo=schedule.start.tzinfo or pytz.utc,
            )
            return ScheduledSession.create(classroom, start)

    @staticmethod
    def __has_session_today(_schedule) -> bool:
        return DateTimeComparator(
            _schedule.start, datetime.now()
        ).same_date().compare() or (
            _schedule.stop
            and DateTimeComparator(datetime.now(), _schedule.start).same_day().compare()
        )

    @staticmethod
    def today_is_sunday():
        return datetime.now().today().isoweekday() == Weekdays.SUNDAY

    @staticmethod
    def __next_session_on_monday():
        monday: datetime = datetime.now() + timedelta(days=1)
        return monday.isoweekday() == Weekdays.MONDAY
