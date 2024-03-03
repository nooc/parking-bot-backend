from test_fixtures import *


def test_add_carpark_with_success(user_manager, userdata_manager):
    user = user_manager.get_user("user-1")
    carpark = userdata_manager.add_carpark(
        user, CarParkId="abvsdvc", PhoneParkingCode="800"
    )
    assert carpark.Id != None


def test_delete_carpark_with_success(user_manager, userdata_manager) -> None:
    user = user_manager.get_user("user-1")
    assert userdata_manager.remove_carpark(user, 1) == 1


def test_add_kiosk_with_success(user_manager, userdata_manager):
    user = user_manager.get_user("user-1")
    kiosk = userdata_manager.add_kiosk(user, KioskId="abvsdvc")
    assert kiosk.Id != None


def test_delete_kiosk_with_success(user_manager, userdata_manager) -> None:
    user = user_manager.get_user("user-1")
    assert userdata_manager.remove_kiosk(user, 1) == 1


def test_list_carparks(user_manager, userdata_manager):
    user = user_manager.get_user("user-2")
    assert userdata_manager.list_carparks(user) != []
