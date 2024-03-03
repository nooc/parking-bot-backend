from typing import Optional

from pydantic import BaseModel, ConfigDict


class SelectedCarPark(BaseModel):
    """User carpark relation for storing user selelcted carparks."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: Optional[int] = None
    UserId: str
    CarParkId: str
    PhoneParkingCode: str


class SelectedKioskPark(BaseModel):
    """User carpark relation for storing user selelcted carparks."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: Optional[int] = None
    UserId: str
    KioskId: str


class CarParks(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Toll: list[SelectedCarPark]
    Kiosk: list[SelectedKioskPark]
