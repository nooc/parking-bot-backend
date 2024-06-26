from datetime import UTC, datetime

from test_fixtures import *

from app.models.user import User, UserState


def test_add_item_success(history_manager):
    user = User(Id="xxyy", State=UserState.Normal, Phone="0700", Roles=["user"])
    item = history_manager.log(
        user=user,
        parking_code="123",
        device_id="123",
        license_plate="abc123",
        type="start-sms",
        timestamp=int(datetime.now(UTC).timestamp()),
    )
    assert item.Id != None


def test_list_items_success(history_manager):
    user = User(Id="xxyy", State=UserState.Normal, Phone="0700", Roles=["user"])
    history_manager.list(user)
