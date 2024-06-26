import pytest
from test_fixtures import *

from app.models.user import User, UserState

SESSION_USER = "user-xyz"
UNKNOWN_USER = "user-foo"


def test_create_user_with_success(user_manager):
    u = user_manager.create_user(Id=SESSION_USER)
    assert u.Id == id


def test_get_user_with_fail(user_manager):
    with pytest.raises(FileNotFoundError):
        user_manager.get_user(UNKNOWN_USER)


def test_get_user_with_success(user_manager):
    u = user_manager.get_user(SESSION_USER)
    assert u.Id == SESSION_USER


def test_update_user(user_manager):
    data = {
        "Id": SESSION_USER,
        "State": UserState.Normal,
        "Roles": ["user"],
        "Phone": "0701234567",
    }
    u0 = User(**data)
    u1 = user_manager.update_user(u0, Phone="0766")
    assert u0.Id == u1.Id and u1.Phone == "0766"


def test_delete_user(user_manager) -> None:
    user_manager.delete_user(SESSION_USER)
    with pytest.raises(Exception):
        user_manager.get_user(SESSION_USER)


def test_list_users(user_manager):
    user_manager.create_user(Id=SESSION_USER + "-0")
    assert user_manager.list_users() != []
