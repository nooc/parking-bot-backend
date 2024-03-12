from test_fixtures import *

from app.models.user import User


def test_log_success(log_manager):
    user = User(Id="user-test-log", State=0, Phone="0700", Roles=["user"])
    log_manager.log(
        user=user,
        ParkingCode="123",
        DeviceId="123",
        LicensePlate="abc123",
        Type="start-sms",
    )


def test_list_success(log_manager):
    user = User(Id="user-1", State=0, Phone="0700", Roles=["user"])
    assert log_manager.list(user=user) != []
