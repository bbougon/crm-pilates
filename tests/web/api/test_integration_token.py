from fastapi import Response, status
from fastapi.testclient import TestClient

from crm_pilates.infrastructure.services import concrete_authentication_service
from crm_pilates.main import app
from tests.faker.custom_authentication_service import (
    CustomAuthenticationService,
    UnauthorizedAuthenticationService,
)

client = TestClient(app)


def test_should_create_token_for_user(authenticated_user):
    app.dependency_overrides[
        concrete_authentication_service
    ] = CustomAuthenticationService

    response: Response = client.post(
        "/token", {"username": "John", "password": "pass", "scope": "bearer"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"token": "my-token", "type": "bearer"}


def test_should_return_unauthorized_if_authentication_fails():
    app.dependency_overrides[
        concrete_authentication_service
    ] = UnauthorizedAuthenticationService

    response: Response = client.post(
        "/token", {"username": "John", "password": "pass", "scope": "bearer"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": [{"msg": "Incorrect username or password", "type": "authenticate"}]
    }
