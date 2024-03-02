from test_fixtures import *


def test_add_carpark_with_success(user_manager, userdata_manager):
    user = user_manager.get_user("user-1")
    carpark = userdata_manager.add_carpark(
        user, CarParkId="abvsdvc", PhoneParkingCode="800"
    )
    assert carpark.Id != None


def test_delete_carpark_with_success(userdata_manager) -> None:
    user = user_manager.get_user("user-1")
    userdata_manager.remove_carpark(user, 1)


def test_list_carparks(user_manager):
    user = user_manager.get_user("user-2")
    assert userdata_manager.list_carparks(user) != []
