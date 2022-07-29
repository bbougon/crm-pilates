from crm_pilates.authenticating.authenticatinguser import AuthenticatingUser
from crm_pilates.authenticating.authentication import Token
from crm_pilates.infrastructure.authentication.JWTAuthenticationService import JWTAuthenticationService
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import UserBuilderForTest
from immobilus import immobilus


@immobilus("2022-07-29T16:12:08.473979")
def test_should_authenticate_user_by_creating_a_JWT_token(memory_repositories):
    RepositoryProvider.write_repositories.user.persist(UserBuilderForTest().username("charles").password("password").build())
    token: Token = JWTAuthenticationService().authenticate(AuthenticatingUser("charles", "password"))

    assert token.token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjaGFybGVzIiwiZXhwaXJlIjoiMjAyMi0wNy0yOVQxNjo0MjowOC40NzM5NzkifQ.ApB012Q9g6ohPGtRPFezTxclicClsmXYYywLOaJ8N6g"
