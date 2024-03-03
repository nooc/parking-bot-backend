from typing import Any, List

from fastapi import APIRouter, Body, Depends, Path, status

from app.dependencies import get_user, get_userdata_manager
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleCreate, VehicleUpdate
from app.services.userdata_manager import UserdataManager

router = APIRouter()


@router.get("/list", status_code=status.HTTP_200_OK)
def list_vehicles(
    udata: UserdataManager = Depends(get_userdata_manager),
    current_user: User = Depends(get_user),
) -> List[Vehicle]:
    return udata.list_vehicles(current_user)


@router.post("/add", status_code=status.HTTP_200_OK)
def add_vehicle(
    udata: UserdataManager = Depends(get_userdata_manager),
    current_user: User = Depends(get_user),
    add: VehicleCreate = Body(title="Vehicle to add."),
) -> Vehicle:
    return udata.add_vehicle(current_user, Vehicle(**add.model_dump()))


@router.post("/update/{vehicle_id}", status_code=status.HTTP_200_OK)
def update_vehicle(
    udata: UserdataManager = Depends(get_userdata_manager),
    current_user: User = Depends(get_user),
    vehicle_id: int = Path(title="Vehicle id"),
    update: VehicleUpdate = Body(title="Vehicle data to update."),
) -> Vehicle:
    return udata.update_vehicle(current_user, vehicle_id, update)


@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
def delete_vehicle(
    udata: UserdataManager = Depends(get_userdata_manager),
    id: int = Path(title="vehicle id"),
    current_user: User = Depends(get_user),
) -> Any:
    udata.remove_vehicle(current_user, id)
