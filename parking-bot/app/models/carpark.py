from typing import Optional

from pydantic import BaseModel, ConfigDict


class SelectedTollPark(BaseModel):
    """User carpark relation for storing user selelcted carparks."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: Optional[int] = None
    CarParkId: str
    PhoneParkingCode: str


class SelectedKioskPark(BaseModel):
    """User carpark relation for storing user selelcted carparks."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)
    Id: Optional[int] = None
    KioskId: str


class SelectedTollParkDb(SelectedTollPark):
    UserId: str


class SelectedKioskParkDb(SelectedKioskPark):
    UserId: str


class CarParks(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Toll: list[SelectedTollPark]
    Kiosk: list[SelectedKioskPark]
