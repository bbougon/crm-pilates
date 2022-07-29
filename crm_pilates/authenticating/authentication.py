from abc import abstractmethod
from dataclasses import dataclass

from crm_pilates.authenticating.authenticatinguser import AuthenticatingUser


class AuthenticationService:

    @abstractmethod
    def authenticate(self, user: AuthenticatingUser):
        pass


@dataclass
class Token:
    token: str
    bearer: str = "bearer"
