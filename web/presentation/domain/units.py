from domain.classroom.duration import HourTimeUnit, MinuteTimeUnit


class Units:

    @staticmethod
    def units():
        return {
            HourTimeUnit.__name__: "HOUR",
            MinuteTimeUnit.__name__: "MINUTE"
        }
