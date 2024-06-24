from datetime import UTC, datetime

from test_fixtures import *

from app.models.user import User, UserState


def test_log_success(history_manager):
    user = User(Id="xxyy", State=UserState.Normal, Phone="0700", Roles=["user"])
    stop = int(datetime.now(UTC).timestamp())
    log = history_manager.log(
        user=user,
        ParkingCode="123",
        DeviceId="123",
        LicensePlate="abc123",
        Type="start-sms",
        Start=stop - 3600,
        Stop=stop,
    )
    assert log.Id != None


def test_list_success(history_manager):
    user = User(Id="xxyy", State=UserState.Normal, Phone="0700", Roles=["user"])
    assert history_manager.list(user) != []
