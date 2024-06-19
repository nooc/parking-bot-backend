from typing import Any, List

from fastapi import APIRouter, Body, Depends, Path, Query, status

from app.dependencies import get_carpark_data, get_user, get_userdata_manager
from app.models.carpark import CarParks, SelectedKioskPark, SelectedTollPark
from app.models.user import User
from app.services.gothenburg_open_data import CarParkDataSource
from app.services.userdata_manager import UserdataManager

router = APIRouter()


@router.post("", status_code=status.HTTP_200_OK)
def request_parking() -> Any:
    """Request parking.
    Create parking entry and send notification to app.

    Toll parking:

    App gets parking-id and can start parking using sms.

    Kiosk parking

    Try parking using kiosk and send result to  .....

    Returns:
        Any: _description_
    """
    pass


@router.delete("", status_code=status.HTTP_200_OK)
def stop_parking() -> Any:
    """Stop parking.

    Returns:
        Any: _description_
    """
    pass
