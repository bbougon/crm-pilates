from command.command_bus import CommandBus
from domain.classroom.session.session_checkin_saga_handler import SessionCheckedIn
from domain.commands import DecreaseClientCreditsCommand
from event.event_bus import EventSubscriber


class SessionCheckedInEventSubscriber(EventSubscriber):

    def __init__(self, command_bus: CommandBus) -> None:
        super().__init__("SessionCheckedIn")
        self.command_bus = command_bus

    def consume(self, event: SessionCheckedIn):
        self.command_bus.send(DecreaseClientCreditsCommand(event.root_id, event.checked_in_attendee))
