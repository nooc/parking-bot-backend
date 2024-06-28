from typing import List

from fastapi import APIRouter, Body, Depends, Path, status

from app.dependencies import get_user, get_vehicle_manager
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleAdd, VehicleUpdate
from app.services.vehicle_manager import VehicleManager

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
def list_vehicles(
    vm: VehicleManager = Depends(get_vehicle_manager),
    current_user: User = Depends(get_user),
) -> List[Vehicle]:
    vehicles_db = vm.list_vehicles(current_user)
    return [Vehicle(**v.model_dump()) for v in vehicles_db]


@router.post("", status_code=status.HTTP_200_OK)
def add_vehicle(
    vm: VehicleManager = Depends(get_vehicle_manager),
    current_user: User = Depends(get_user),
    add: VehicleAdd = Body(title="Vehicle to add."),
) -> Vehicle:
    vehicle_db = vm.add_vehicle(current_user, Vehicle(**add.model_dump()))
    return Vehicle(**vehicle_db.model_dump())


@router.put("/{vehicle_id}", status_code=status.HTTP_200_OK)
def update_vehicle(
    vm: VehicleManager = Depends(get_vehicle_manager),
    current_user: User = Depends(get_user),
    vehicle_id: int = Path(title="Vehicle id"),
    update: VehicleUpdate = Body(title="Vehicle data to update."),
) -> Vehicle:
    return vm.update_vehicle(current_user, vehicle_id, **update.model_dump())


@router.delete("/{vehicle_id}", status_code=status.HTTP_200_OK)
def delete_vehicle(
    vm: VehicleManager = Depends(get_vehicle_manager),
    vehicle_id: int = Path(title="vehicle id"),
    current_user: User = Depends(get_user),
) -> None:
    vm.remove_vehicle(vehicle_id)
