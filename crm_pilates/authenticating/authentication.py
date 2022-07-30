from abc import abstractmethod
from dataclasses import dataclass

from crm_pilates.authenticating.authenticating_user import AuthenticatingUser


class AuthenticationException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AuthenticationService:
    @abstractmethod
    def authenticate(self, user: AuthenticatingUser):
        pass

    @abstractmethod
    def load_token(self, token: str):
        pass

    @abstractmethod
    def validate_token(self):
        pass


@dataclass
class Token:
    token: str
    type: str = "bearer"
