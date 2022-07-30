from crm_pilates.authenticating.authenticating_user import AuthenticatingUser
from crm_pilates.authenticating.authentication import Token, AuthenticationException
from crm_pilates.infrastructure.authentication.JWTAuthenticationService import (
    JWTAuthenticationService,
)
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import UserBuilderForTest
from immobilus import immobilus
import pytest


@immobilus("2022-07-29T16:12:08.473979")
def test_should_authenticate_user_by_creating_a_JWT_token(memory_repositories):
    RepositoryProvider.write_repositories.user.persist(
        UserBuilderForTest().username("charles").password("password").build()
    )
    token: Token = JWTAuthenticationService().authenticate(
        AuthenticatingUser("charles", "password")
    )

    assert (
        token.token
        == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjaGFybGVzIiwiZXhwIjoxNjU5MTEyOTI4fQ.u3ig8KW8yBmWa3awfqpwf__1sxHJHvOdBlmWpu1SxMw"
    )


def test_should_raise_authentication_exception_when_password_is_wrong(
    memory_repositories,
):
    with pytest.raises(AuthenticationException):
        RepositoryProvider.write_repositories.user.persist(
            UserBuilderForTest().username("charles").password("password").build()
        )
        JWTAuthenticationService().authenticate(
            AuthenticatingUser("charles", "wrong-password")
        )


@immobilus("2022-07-29T16:22:08.473979")
def test_should_validate_token(memory_event_store):
    RepositoryProvider.write_repositories.user.persist(
        UserBuilderForTest().username("charles").password("password").build()
    )
    jwt_authentication_service = JWTAuthenticationService()

    jwt_authentication_service.load_token(
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjaGFybGVzIiwiZXhwIjoxNjU5MTEyOTI4fQ.u3ig8KW8yBmWa3awfqpwf__1sxHJHvOdBlmWpu1SxMw"
    )
    jwt_authentication_service.validate_token()


@immobilus("2022-07-29T16:22:08.473979")
def test_should_not_validate_token_when_not_signed_with_private_key(memory_event_store):
    with pytest.raises(AuthenticationException) as e:
        RepositoryProvider.write_repositories.user.persist(
            UserBuilderForTest().username("charles").password("password").build()
        )
        jwt_authentication_service = JWTAuthenticationService()

        jwt_authentication_service.load_token(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjaGFybGVzIiwiZXhwaXJlIjoiMjAyMi0wNy0yOVQxNjo0MjowOC40NzM5NzkifQ.XjOYrRWqxCMujBUd2RjdQnV-TTdReVn-MKq_xYkXyL0"
        )
        jwt_authentication_service.validate_token()

    assert e.value.message == "Invalid token provided"


@immobilus("2022-07-29T16:22:08.473979")
def test_should_not_validate_token_when_unexpected_payload(memory_event_store):
    with pytest.raises(AuthenticationException) as e:
        RepositoryProvider.write_repositories.user.persist(
            UserBuilderForTest().username("charles").password("password").build()
        )
        jwt_authentication_service = JWTAuthenticationService()

        jwt_authentication_service.load_token(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ3cm9uZy1lbnRyeSI6ImJhYWFkIiwiZXhwaXJlIjoiMjAyMi0wNy0yOVQxNjo0MjowOC40NzM5NzkifQ.d2OAvH3B51xYWVqn6TVOEs0rCrthZLVQ68hUwX0OU8s"
        )
        jwt_authentication_service.validate_token()

    assert e.value.message == "Invalid token provided"


@immobilus("2022-07-29T16:22:08.473979")
def test_should_not_validate_token_when_user_is_not_found(memory_event_store):
    with pytest.raises(AuthenticationException) as e:
        RepositoryProvider.write_repositories.user.persist(
            UserBuilderForTest().username("Henri").password("password").build()
        )
        jwt_authentication_service = JWTAuthenticationService()

        jwt_authentication_service.load_token(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjaGFybGVzIiwiZXhwIjoiMjAyMi0wNy0yOVQxNjo0MjowOC40NzM5NzkifQ.xC-yioYqk5hxRSuBjzb5I3RuyZq0tKDRMXl39rgYABM"
        )
        jwt_authentication_service.validate_token()

    assert e.value.message == "Invalid token provided"


@immobilus("2022-07-29T16:22:08.473979")
def test_should_not_validate_if_token_expired(memory_event_store):
    with pytest.raises(AuthenticationException) as e:
        RepositoryProvider.write_repositories.user.persist(
            UserBuilderForTest().username("Henri").password("password").build()
        )
        jwt_authentication_service = JWTAuthenticationService()

        jwt_authentication_service.load_token(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjaGFybGVzIiwiZXhwIjoxNjU5MTAyOTI4fQ.Utk5qODV20JyXVBUsa6NmTWV0hMwvfQ-7QqE5I5IXtI"
        )
        jwt_authentication_service.validate_token()

    assert e.value.message == "Token expired"
