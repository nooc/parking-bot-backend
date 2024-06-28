import base64
from typing import Any

from fastapi import APIRouter, Body, Depends, Path, status

from app.dependencies import get_parking_manager, get_user
from app.models.parking import ParkingRequest
from app.models.user import User
from app.services.parking_manager import ParkingManager

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    description="""
             Request parking at car park and return push notification
             containing id associated with the parking.
             For toll parking, app initiates sms parking on success.
             For kiosk, try parking and respond with id and time info.
             """,
)
def request_parking(
    parking_request: ParkingRequest = Body(description="Parking request"),
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
    parking_mgr.request(
        user=current_user,
        carpark_id=parking_request.CarParkId,
        vehicle_id=parking_request.VehicleId,
    )


@router.get(
    "/retry/{payload}",
    status_code=status.HTTP_200_OK,
    description="""Retry kiosk""",
)
def request_parking(
    retry_payload: str = Path(
        description="Retry payload as an url safe base64 of ParkingRequest json"
    ),
    current_user: User = Depends(get_user),
    parking_mgr: ParkingManager = Depends(get_parking_manager),
) -> Any:
    # decode retry payload as ParkingRequest
    retry_request = ParkingRequest.model_validate_json(
        base64.urlsafe_b64decode(retry_payload)
    )
    parking_mgr.request(
        user=current_user,
        carpark_id=retry_request.CarParkId,
        vehicle_id=retry_request.VehicleId,
    )


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
