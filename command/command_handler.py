from abc import abstractmethod

from command.command import Command

class CommandHandler:

    @abstractmethod
    def execute(self, command: Command) -> None:
        ...