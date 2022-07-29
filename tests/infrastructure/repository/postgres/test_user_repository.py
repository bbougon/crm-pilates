import pytest

from crm_pilates import settings
from crm_pilates.authenticating.domain.user import User
from crm_pilates.domain.exceptions import AggregateNotFoundException
from crm_pilates.infrastructure.repository.postgres.user_repository import (
    PostgresUserRepository,
)


def test_should_return_desired_user(clean_database):
    PostgresUserRepository(settings.DATABASE_URL).persist(User("John", "doepassword"))

    user: User = PostgresUserRepository(settings.DATABASE_URL).get_by_username("John")

    assert user is not None
    assert user.username == "John"
    assert user.password == "doepassword"


def test_should_raise_exception_if_user_not_found(clean_database):
    with pytest.raises(AggregateNotFoundException):
        PostgresUserRepository(settings.DATABASE_URL).get_by_username("John")
