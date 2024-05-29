from datetime import UTC, datetime

from test_fixtures import *

from app.models.user import User, UserState


def test_log_success(log_manager):
    user = User(Id="0a0a0a0a0a0a0a11", State=0, Phone="0700", Roles=["user"])
    stop = int(datetime.now(UTC).timestamp())
    log_manager.log(
        user=user,
        ParkingCode="123",
        DeviceId="123",
        LicensePlate="abc123",
        Type="start-sms",
        Start=stop - 3600,
        Stop=stop,
    )


def test_list_success(log_manager):
    user = User(
        Id="0a0a0a0a0a0a0a01", State=UserState.Normal, Phone="0700", Roles=["user"]
    )
    assert log_manager.list(user=user) != []
