from fastapi import status
from test_fixtures import *


def test_read_user_with_no_token_should_fail(server_with_mock_db):
    response = server_with_mock_db.get(url="/user")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_read_user_with_token_should_succeed(server_with_mock_db, test_auth):
    response = server_with_mock_db.get(url="/user", auth=test_auth)
    assert response.status_code == status.HTTP_200_OK


def test_register_user_with_token_should_succeed(
    server_with_mock_db, test_auth_no_user
):
    response = server_with_mock_db.post(
        url="/user/register", auth=test_auth_no_user, json={"Phone": "0123456789"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["Id"] == "john_doe"
