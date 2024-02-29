from typing import Any

from fastapi import APIRouter, Body, Depends, Path, status

from app.dependencies import get_open_data_service, get_user, get_userdata_manager
from app.models.carpark import CarParkSelect, SelectedCarPark
from app.models.user import User
from app.services.open_data_parking import OpenDataParking
from app.services.userdata_manager import UserdataManager

router = APIRouter()


@router.get(
    "/list", response_model=list[SelectedCarPark], status_code=status.HTTP_200_OK
)
def list_carparks(
    udata: UserdataManager = Depends(get_userdata_manager),
    current_user: User = Depends(get_user),
) -> Any:
    return udata.list_carparks(current_user)


@router.post("/add", status_code=status.HTTP_200_OK, response_model=SelectedCarPark)
def add_carpark(
    udata: UserdataManager = Depends(get_userdata_manager),
    current_user: User = Depends(get_user),
    opendata: OpenDataParking = Depends(get_open_data_service),
    add: CarParkSelect = Body(title="Car park to add to selection."),
) -> Any:
    park = opendata.get_toll_parking(add.Id)  # check if exists
    return udata.add_carpark(current_user, SelectedCarPark(CarParkId=park.Id))


@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
def delete_carpark(
    udata: UserdataManager = Depends(get_userdata_manager),
    id: int = Path(title="CarPark id"),
    current_user: User = Depends(get_user),
) -> Any:
    udata.remove_carpark(current_user, id)
