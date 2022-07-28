from abc import abstractmethod

from crm_pilates.authenticating.user import User


class AuthenticationService:

    @abstractmethod
    def authenticate(self, user: User):
        pass
