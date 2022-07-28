from crm_pilates.authenticating.authentication import AuthenticationService
from crm_pilates.authenticating.user import User


class CustomAuthenticationService(AuthenticationService):

    def authenticate(self, user: User):
        return {"token": "my-token", "type": "bearer"}
