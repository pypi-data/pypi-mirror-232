MOCK_DATA = {
    "add_user_request":
        {
            "email": "email@example.com",
            "username": "myuser",
            "firstName": "John",
            "lastName": "Doe",
            "credentials": [
                {
                        "value": "password",
                        "type": "password",
                }
            ],
        },
    "add_user_response": {
        "user_data": {
            "some_data": None
        },
        "code": 200
        },
    "delete_user_response": {
        "message": "user_deleted",
        "code": 200
        },
    "connection_args":
        {
            "server_url": "someurl/",
            "username": "someusername",
            "password": "somepassword",
            "realm_name": "somerealm",
            "client_id": "clientID",
            "client_secret_key": "secretkey",
        },
        "mock_public_key": "somemockpublickeyvalue",
        "mock_decoded_token": {"some_info": 100, "user_id": "some_user_id"},
        "get_user_response": {
            "email": "email@example.com",
            "username": "myuser",
            "firstName": "John",
            "lastName": "Doe",
            "credentials": [
                {
                        "value": "password",
                        "type": "password",
                }
            ],
        },
}
