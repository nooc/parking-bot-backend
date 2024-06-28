from datetime import UTC, datetime

from test_fixtures import *

from app.models.user import User, UserState
from app.util.time import get_utc_seconds


def test_add_item_success(history_manager):
    user = User(Id="xxyy", State=UserState.Normal, Phone="0700", Roles=["user"])
    item = history_manager.add(
        user=user,
        type="create-parking",
        timestamp=get_utc_seconds(),
        carpark_id="xyz",
        vehicle_id=10,
    )
    assert item.Id != None


def test_list_items_success(history_manager):
    user = User(Id="xxyy", State=UserState.Normal, Phone="0700", Roles=["user"])
    history_manager.list(user)
