from fastapi import status
from test_fixtures import *


def test_read_user_with_no_token_should_fail(server):
    response = server.get("/user")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_read_user_with_token_should_succeed(server):
    response = server.get("/user")
    assert response.status_code == status.HTTP_200_OK
