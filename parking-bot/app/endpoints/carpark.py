from typing import Any, List

from fastapi import APIRouter, Body, Depends, Path, Query, status

from app.dependencies import get_open_data_service, get_user, get_userdata_manager
from app.models.carpark import (
    CarParks,
    CarParkSelect,
    SelectedCarPark,
    SelectedKioskPark,
)
from app.models.user import User
from app.services.open_data_parking import OpenDataParking
from app.services.userdata_manager import UserdataManager

router = APIRouter()


@router.get("/list", status_code=status.HTTP_200_OK)
def list_carparks(
    udata: UserdataManager = Depends(get_userdata_manager),
    current_user: User = Depends(get_user),
) -> CarParks:
    return CarParks(
        Toll=udata.list_toll_carparks(current_user),
        Kiosk=udata.list_kiosk_carparks(current_user),
    )


@router.post("/add", status_code=status.HTTP_200_OK)
def add_carpark(
    udata: UserdataManager = Depends(get_userdata_manager),
    current_user: User = Depends(get_user),
    opendata: OpenDataParking = Depends(get_open_data_service),
    add: id = Query(title="Car park to add to selection."),
) -> SelectedCarPark:
    carpark = opendata.get_toll_parking(id)  # check if exists
    return udata.add_carpark(current_user, carpark.Id, carpark.PhoneParkingCode)


@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
def delete_carpark(
    udata: UserdataManager = Depends(get_userdata_manager),
    id: int = Path(title="CarPark id"),
    current_user: User = Depends(get_user),
) -> Any:
    udata.remove_carpark(current_user, id)


@router.post("/kiosk/add", status_code=status.HTTP_200_OK)
def add_kiosk(
    udata: UserdataManager = Depends(get_userdata_manager),
    current_user: User = Depends(get_user),
    opendata: OpenDataParking = Depends(get_open_data_service),
    add: id = Query(title="Kiosk park to add to selection."),
) -> SelectedKioskPark:
    kiosk = opendata.get_kiosk_parking(id)  # check if exists
    return udata.add_kiosk(current_user, kiosk.Id)


@router.delete("/kiosk/delete/{id}", status_code=status.HTTP_200_OK)
def delete_kiosk(
    udata: UserdataManager = Depends(get_userdata_manager),
    id: int = Path(title="Kiosk id"),
    current_user: User = Depends(get_user),
) -> Any:
    udata.remove_kiosk(current_user, id)
