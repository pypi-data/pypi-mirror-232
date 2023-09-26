"""
This Module contains the OrodhaKeycloakClient class which is a facade
used to interact with a keycloak server via python-keycloak.
"""
import orodha_keycloak.connections.admin
import orodha_keycloak.connections.client
from orodha_keycloak.connections.exceptions import InvalidConnectionException


class OrodhaKeycloakClient:
    """
        Facade class used for connecting to, and interacting with keycloak for the Orodha
    shopping list app.

    Args:
        server_url(str): The url of the server that our keycloak is hosted at
        realm_name(str): The name of the keycloak realm that we are attempting to access.
        client_id(str): The keycloak client_id that we are using for the connection.
        client_secret_key(str): The secret key of the keycloak client.
        username(str) - Optional: The username of the user being impersonated by python-keycloak
        password(str) - Optional: The password of the user being impersonated by python-keycloak

    Raises:
        InvalidConnectionException: If the connection variables given are invalid
            and do not allow connection.
    """

    def __init__(
        self,
        server_url: str,
        realm_name: str,
        client_id: str,
        client_secret_key: str = None,
        username: str = None,
        password: str = None
    ):
        username_password_auth_available = username and password

        if not client_secret_key and not username_password_auth_available:
            raise InvalidConnectionException(
                ["client_secret_key", "username", "password"],
                message="Must have either client_secret_key or username and password"
            )

        self.client_connection = orodha_keycloak.connections.client.create_client_connection(
            server_url=server_url,
            realm_name=realm_name,
            client_id=client_id,
            client_secret_key=client_secret_key
        )
        if client_secret_key:
            self.admin_connection = orodha_keycloak.connections.admin.create_admin_connection(
                server_url=server_url,
                realm_name=realm_name,
                client_id=client_id,
                client_secret_key=client_secret_key,
            )
        else:
            self.admin_connection = orodha_keycloak.connections.admin.create_admin_connection(
                server_url=server_url,
                realm_name=realm_name,
                username=username,
                password=password
            )

    def add_user(
            self,
            email: str,
            username: str,
            firstName: str,
            lastName: str,
            password: str
    ):
        """
        Adds a user to keycloak with a password.

        Args:
                email(str): The email of the new user.
                username(str): The username of the new user.
                firstName(str): The first name of the new user.
                lastName(str): The last name of the new user.
                password(str): The password of the new user.

        Returns:
            new_user: The new user info genereated by the keycloak server.

        """
        new_user = self.admin_connection.create_user(
            {
                "email": email,
                "username": username,
                "enabled": True,
                "firstName": firstName,
                "lastName": lastName,
                "credentials": [
                    {
                        "value": password,
                        "type": "password",
                    }
                ],
            },
            exist_ok=False,
        )

        return new_user

    def delete_user(self, user_id):
        """
        Deletes a keycloak user with a given user_id.

        Args:
            user_id(str): The user id of the user to be deleted.

        Returns:
            response: The response from the keycloak server with info about the deletion.
        """
        response = self.admin_connection.delete_user(user_id=user_id)

        return response

    def get_user(self, token: str = None, user_id: str = None):
        """
        Takes either a user_id or a token and returns the user if they exist.

        Args:
            user_id(str): String user id of our user, is used to access keycloak in a query.
            token(str): Our JWT token that we will use to decode and obtain the user from.

        Returns:
            user: The user, if any, that is associated with this user_identification value.
        """

        if token:
            return_value = self.admin_connection.get_user(
                self.decode_jwt(token).get("sub"))
        else:
            return_value = self.admin_connection.get_user(user_id)

        return return_value

    def decode_jwt(self, token):
        """
        Small helper function which decodes a JWT token using the client connection.

        Args:
            token(str): A JWT token that we get from keycloak.

        Returns:
            token_info(dict): The decoded information from the token.
        """
        keycloak_public_key = "-----BEGIN PUBLIC KEY-----\n" + \
            self.client_connection.public_key() + "\n-----END PUBLIC KEY-----"
        options = {
            "verify_signature": True,
            "verify_aud": False,
            "verify_exp": True
        }
        token_info = self.client_connection.decode_token(
            token,
            key=keycloak_public_key,
            options=options)
        return token_info
