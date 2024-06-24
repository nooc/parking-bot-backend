from typing import Any, List

from fastapi import APIRouter, Body, Depends, Path, Query, status

from app.dependencies import (
    get_carpark_manager,
    get_dggs,
    get_kiosk,
    get_user,
    get_userdata_manager,
)
from app.models.carpark import CarPark
from app.models.external.kiosk import KioskParkingCreate
from app.models.user import User
from app.services.carpark_manager import CarParkManager
from app.services.kiosk_manager import KioskManager
from app.services.userdata_manager import UserdataManager
from app.util.dggs import Dggs

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
def list_selected_carpark_ids(
    current_user: User = Depends(get_user),
) -> list[str]:
    return current_user.CarParks


@router.post("/{id}", status_code=status.HTTP_200_OK)
def select_carpark(
    udata: UserdataManager = Depends(get_userdata_manager),
    current_user: User = Depends(get_user),
    cpdata: CarParkManager = Depends(get_carpark_manager),
    id: str = Path(title="Car park id to add to selection."),
) -> None:
    udata.add_carpark(user=current_user, carpark_id=id)


@router.delete("/toll/{id}", status_code=status.HTTP_200_OK)
def delete_carpark(
    udata: UserdataManager = Depends(get_userdata_manager),
    id: int = Path(title="CarPark id"),
    current_user: User = Depends(get_user),
) -> Any:
    udata.remove_tollpark(user=current_user, carpark_id=id)


@router.post("/kiosk", status_code=status.HTTP_200_OK)
def add_kiosk(
    current_user: User = Depends(get_user),
    kiosk: KioskManager = Depends(get_kiosk),
    new_kiosk: KioskParkingCreate = Body(title="Kiosk parking to add to known kiosks."),
) -> None:
    kiosk.try_add_to_known_kiosks(
        id=new_kiosk.Id, lat=new_kiosk.Lat, lon=new_kiosk.Long
    )


@router.put("/kiosk", status_code=status.HTTP_200_OK)
def update_kiosk(
    current_user: User = Depends(get_user),
    kiosk: KioskManager = Depends(get_kiosk),
    new_kiosk: KioskParkingCreate = Body(title="Kiosk parking to update."),
) -> None:
    kiosk.update_kiosks(id=new_kiosk.Id, lat=new_kiosk.Lat, lon=new_kiosk.Long)


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
    cpdata: CarParkManager = Depends(get_carpark_manager),
    cell: float = Path(title="Cell id"),
    current_user: User = Depends(get_user),
) -> list[CarPark]:
    return cpdata.get_carparks_by_cell_id(cell)
