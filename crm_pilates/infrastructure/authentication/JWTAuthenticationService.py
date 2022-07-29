from datetime import timedelta, datetime

from jose import jwt
from passlib.context import CryptContext

from crm_pilates.authenticating.authenticatinguser import AuthenticatingUser
from crm_pilates.authenticating.authentication import AuthenticationService, Token
from crm_pilates.authenticating.domain.user import User
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from crm_pilates.settings import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTAuthenticationService(AuthenticationService):

    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    def authenticate(self, user: AuthenticatingUser) -> Token:
        retrieved_user: User = RepositoryProvider.write_repositories.user.get_by_username(user.username)
        pwd_context.verify(user.password, retrieved_user.password)
        access_token_expires = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        encoded_jwt = jwt.encode({"sub": retrieved_user.username, "expire": access_token_expires.isoformat()}, config("SECRET_KEY"), algorithm=self.ALGORITHM)
        return Token(encoded_jwt)
