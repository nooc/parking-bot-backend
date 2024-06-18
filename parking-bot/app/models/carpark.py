from typing import Optional,

from pydantic import BaseModel, ConfigDict

from app.models.kiosk_info import KioskInfo
from app.models.toll_info import TollInfo


class ParkingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    # dggs cell this location belongs to
    CellId: str
    # geometry. atleast a point
    Geometry: str

class TollPark(ParkingBase):
    """User carpark relation for storing user selelcted carparks."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: Optional[int] = None
    Info: TollInfo

class KioskPark(ParkingBase):
    """User carpark relation for storing user selelcted carparks."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)
    Id: Optional[int] = None
    Info: KioskInfo

class CarParks(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Toll: list[TollPark]
    Kiosk: list[KioskPark]

class SelectedCarParks(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Toll: Optional[list[int]] = []
    Kiosk: Optional[list[int]] = []
