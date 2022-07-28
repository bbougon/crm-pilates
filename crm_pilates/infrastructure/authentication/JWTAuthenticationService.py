from crm_pilates.authenticating.authentication import AuthenticationService
from crm_pilates.authenticating.user import User


class JWTAuthenticationService(AuthenticationService):
    def authenticate(self, user: User):
        pass
