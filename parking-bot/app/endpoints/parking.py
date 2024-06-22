from typing import Any, List

from fastapi import APIRouter, Body, Depends, Path, Query, status

from app.dependencies import get_parking_manager, get_user
from app.models.user import User
from app.services.gothenburg_open_data import CarParkDataSource
from app.services.parking_manager import ParkingManager
from app.services.userdata_manager import UserdataManager

router = APIRouter()


@router.post(
    "/{id}",
    status_code=status.HTTP_200_OK,
    description="""
             Request parking at car park and return push notification
             containing id associated with the parking.
             For toll parking, app initiates sms parking on success.
             For kiosk, try parking and respond with id and time info.
             """,
)
def request_parking(
    carpark_id: str = Path(description="Parking id"),
    current_user: User = Depends(get_user),
    parking_mgr: ParkingManager = Depends(get_parking_manager),
) -> Any:
    """Request parking.
    Create parking entry and send notification to app.

    Toll parking:

    App gets parking-id and can start parking using sms.

    Kiosk parking

    Try parking using kiosk and send result to  .....

    Returns:
        Any: _description_
    """
    parking_mgr.request(user=current_user, carpark_id=carpark_id)


@router.delete("", status_code=status.HTTP_200_OK)
def stop_parking(
    parking_id: str = Path(description="Parking id"),
    current_user: User = Depends(get_user),
    parking_mgr: ParkingManager = Depends(get_parking_manager),
) -> Any:
    """Stop parking.

    Returns:
        Any: _description_
    """
    parking_mgr.delete(user=current_user, parking_id=parking_id)
