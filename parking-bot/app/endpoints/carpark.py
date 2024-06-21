from typing import Any, List

from fastapi import APIRouter, Body, Depends, Path, Query, status

from app.services.kiosk_manager import KioskManager
import app.util.http_error as err
from app.dependencies import (
    get_carpark_data,
    get_carparkdata_manager,
    get_dggs,
    get_kiosk,
    get_user,
    get_userdata_manager,
)
from app.models.carpark import CarPark, SelectedCarParks
from app.models.user import User
from app.services.car_park_data import CarParkDataManager
from app.services.gothenburg_open_data import CarParkDataSource
from app.services.userdata_manager import UserdataManager
from app.util.dggs import Dggs

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
def list_carparks(
    current_user: User = Depends(get_user),
) -> SelectedCarParks:
    return current_user.CarParks


@router.post("/toll", status_code=status.HTTP_200_OK)
def add_tollpark(
    udata: UserdataManager = Depends(get_userdata_manager),
    current_user: User = Depends(get_user),
    carpark_dat: CarParkDataSource = Depends(get_carpark_data),
    id: str = Query(title="Car park to add to selection."),
) -> None:
    carpark_dat.get_toll_parking(id)  # check if exists
    udata.add_tollpark(user=current_user, carpark_id=id)


@router.delete("/toll/{id}", status_code=status.HTTP_200_OK)
def delete_carpark(
    udata: UserdataManager = Depends(get_userdata_manager),
    id: int = Path(title="CarPark id"),
    current_user: User = Depends(get_user),
) -> Any:
    udata.remove_tollpark(user=current_user, carpark_id=id)


@router.post("/kiosk", status_code=status.HTTP_200_OK)
def add_kiosk(
    udata: UserdataManager = Depends(get_userdata_manager),
    current_user: User = Depends(get_user),
    kiosk: KioskManager = Depends(get_kiosk),
    id: str = Query(title="Kiosk park to add to selection."),
) -> None:
    # TODO: check kiosk exists (try fetch kiosk info)
    kiosk.
    udata.add_kioskpark(user=current_user, carpark_id=id)


@router.delete("/kiosk/{id}", status_code=status.HTTP_200_OK)
def delete_kiosk(
    udata: UserdataManager = Depends(get_userdata_manager),
    id: int = Path(title="Kiosk id"),
    current_user: User = Depends(get_user),
) -> Any:
    udata.remove_kioskpark(user=current_user, carpark_id=id)


@router.get(
    "/geo",
    status_code=status.HTTP_200_OK,
    summary="Get set of cells at lat/lon coordinate.",
)
def get_cells(
    dggs: Dggs = Depends(get_dggs),
    lat: float = Query(title="Latitude"),
    lon: float = Query(title="Longitude"),
    current_user: User = Depends(get_user),
) -> list[str]:
    return dggs.lat_lon_to_cells(lat=lat, lon=lon, include_neighbors=True)


@router.get(
    "/geo/{cell}",
    status_code=status.HTTP_200_OK,
    summary="Get cell content by cell id.",
)
def get_cell_content(
    cpdata: CarParkDataManager = Depends(get_carparkdata_manager),
    cell: float = Path(title="Cell id"),
    current_user: User = Depends(get_user),
) -> list[CarPark]:
    return cpdata.get_carparks_by_cell_id(cell)
