from fastapi.security import OAuth2PasswordRequestForm

from crm_pilates.infrastructure.services import concrete_authentication_service
from crm_pilates.web.api.token import create_token
from tests.faker.custom_authentication_service import CustomAuthenticationService


def test_should_create_token_for_user(mocker):
    mocker.patch("tests.web.test_token.concrete_authentication_service", new_callable=CustomAuthenticationService)

    response = create_token(OAuth2PasswordRequestForm(username="John", password="pass", scope="bearer"), concrete_authentication_service)

    assert response == {"token": "my-token", "type": "bearer"}
