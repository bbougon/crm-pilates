from crm_pilates.infrastructure.services import concrete_authentication_service
from crm_pilates.web.api.authentication import authentication_service


def test_authentication_service_has_token_loaded(mocker):
    mocker.patch("tests.web.api.test_authentication.concrete_authentication_service")

    authentication_service("a-token", concrete_authentication_service)

    concrete_authentication_service.validate_token.assert_called_once_with("a-token")
