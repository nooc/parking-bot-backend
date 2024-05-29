import jwt
from fastapi import status
from test_fixtures import *


def test_register_user_with_token_should_succeed(
    server_with_mock_db, test_auth_init, settings
):
    response = server_with_mock_db.post(url="/user/init", auth=test_auth_init)
    assert response.status_code == status.HTTP_200_OK
    jwt.decode(
        jwt=response.text,
        key=settings.HS256_KEY,
        algorithms=["HS256"],
        issuer=settings.JWT_ISSUER,
        verify=True,
        audience=settings.JWT_AUDIENCE,
    )


def test_read_user_with_no_token_should_fail(server_with_mock_db):
    response = server_with_mock_db.get(url="/user")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_read_user_with_invalid_token_should_fail(
    server_with_mock_db, test_auth_invalid
):
    response = server_with_mock_db.get(url="/user", auth=test_auth_invalid)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_read_user_with_token_should_succeed(server_with_mock_db, test_auth):
    response = server_with_mock_db.get(url="/user", auth=test_auth)
    assert response.status_code == status.HTTP_200_OK
