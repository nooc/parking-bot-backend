import pytest
from test_fixtures import *

from app.models.user import User, UserState


def test_create_user_with_success(user_manager):
    id = "user-new"
    u = user_manager.create_user(Id=id, Phone="0700")
    assert u.Id == id


def test_get_user_with_fail(user_manager):
    with pytest.raises(FileNotFoundError):
        user_manager.get_user("user-none")


def test_get_user_with_success(user_manager):
    u = user_manager.get_user("user-1")
    assert u.Id == "user-1"


def test_update_user(user_manager):
    u0 = User(Id="user-2", State=UserState.Normal, Roles=["user"], Phone="0701234567")
    u = user_manager.update_user(u0, Phone="0766")
    assert u.Phone == "0766"


def test_delete_user(user_manager) -> None:
    user_manager.delete_user("user-3")
    with pytest.raises(Exception):
        user_manager.get_user("user-3")


def test_list_users(user_manager):
    assert user_manager.list_users() != []
