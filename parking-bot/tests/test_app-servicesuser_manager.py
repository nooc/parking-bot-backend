from test_fixtures import *

from app.models.user import User, UserCreate, UserState, UserUpdate


def test_create_user_with_success(user_manager):
    id = "test-user-new"
    u = user_manager.create_user(UserCreate(Id=id))
    assert u.Id == id


def test_get_user_with_fail(user_manager):
    with pytest.raises(FileNotFoundError):
        user_manager.get_user("test-user-none")


def test_get_user_with_success(user_manager):
    u = user_manager.get_user("test-user-1")
    assert u.Id == "test-user-1"


def test_update_user(user_manager):
    u = user_manager.update_user(
        User(Id="test-user-2", State=0, Roles=["user"]),
        UserUpdate(State=UserState.Disabled),
    )
    assert u.State == UserState.Disabled


def test_delete_user(user_manager) -> None:
    user_manager.delete_user(User(Id="test-user-3", State=0, Roles=["user"]))


def test_list_users(user_manager):
    assert user_manager.list_users() != []
