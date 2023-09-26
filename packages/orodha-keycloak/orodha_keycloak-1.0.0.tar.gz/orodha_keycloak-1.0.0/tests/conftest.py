"""
This module contains two fixtures which supply our mock admin connections to
our OrodhaKeycloakClient in lieu of using the python-keycloak package to connect to our server.
"""
from unittest.mock import MagicMock
import pytest
from tests.fixtures.keycloak import MOCK_DATA


class MockKeycloakAdmin:
    """Mocked Admin KeycloakOpenIdConnection object used to mock admin
        keycloak functions in testing."""

    def __init__(self, **kwargs):
        self.arguments = dict(kwargs)

    def create_user(self, *args, **kwargs):
        return MOCK_DATA["add_user_response"]

    def delete_user(self, *args, **kwargs):
        return MOCK_DATA.get("delete_user_response")

    def get_user(self, *args, **kwargs):
        return MOCK_DATA.get("get_user_response")


class MockKeycloakClient:
    """Mocked Client KeycloakOpenId object used to mock client keycloak functions in testing."""

    def __init__(self, **kwargs):
        self.arguments = dict(kwargs)

    def public_key(self):
        return MOCK_DATA["mock_public_key"]

    def decode_token(self, *args, **kwargs):
        return MOCK_DATA.get("mock_decoded_token")


@pytest.fixture
def mock_create_client_connection(mocker):
    """
    Fixture which patches our create_client_connection function to return our mocked client.
    """
    mocker.patch(
        "orodha_keycloak.connections.client.create_client_connection",
        return_value=MockKeycloakClient(),
    )


@pytest.fixture
def mock_create_admin_connection(mocker):
    """
    Fixture which patches our create_admin_connection function to return our mocked client.
    """
    mocker.patch(
        "orodha_keycloak.connections.admin.create_admin_connection",
        return_value=MockKeycloakAdmin(),
    )
