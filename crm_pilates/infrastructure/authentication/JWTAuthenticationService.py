from datetime import timedelta, datetime

from jose import ExpiredSignatureError, jwt, JWTError
from passlib.context import CryptContext

from crm_pilates.authenticating.authenticating_user import AuthenticatingUser
from crm_pilates.authenticating.authentication import (
    AuthenticationService,
    Token,
    AuthenticationException,
)
from crm_pilates.authenticating.domain.user import User
from crm_pilates.domain.exceptions import AggregateNotFoundException
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from crm_pilates.settings import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTAuthenticationService(AuthenticationService):

    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    def __init__(self) -> None:
        super().__init__()
        self.__token = ""

    def authenticate(self, user: AuthenticatingUser) -> Token:
        retrieved_user: User = (
            RepositoryProvider.write_repositories.user.get_by_username(user.username)
        )
        if not pwd_context.verify(user.password, retrieved_user.password):
            raise AuthenticationException
        access_token_expires = datetime.utcnow() + timedelta(
            minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        encoded_jwt = jwt.encode(
            {
                "sub": retrieved_user.username,
                "exp": access_token_expires,
            },
            config("SECRET_KEY"),
            algorithm=self.ALGORITHM,
        )
        return Token(encoded_jwt)

    def load_token(self, token: str):
        self.__token = token

    def validate_token(self):
        try:
            decoded_jwt = jwt.decode(
                self.__token, config("SECRET_KEY"), algorithms=[self.ALGORITHM]
            )
            username: str = decoded_jwt.get("sub")
            if username is None:
                raise AuthenticationException("Invalid token provided")
            RepositoryProvider.write_repositories.user.get_by_username(username)
        except ExpiredSignatureError:
            raise AuthenticationException("Token expired")
        except (JWTError, AggregateNotFoundException):
            raise AuthenticationException("Invalid token provided")
