from abc import abstractmethod

from command.response import Event


class Command:
    pass


class CommandHandler:

    @abstractmethod
    def execute(self, command: Command) -> Event:
        ...