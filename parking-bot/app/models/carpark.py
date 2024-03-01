from typing import Optional

from pydantic import BaseModel, ConfigDict


class SelectedCarPark(BaseModel):
    """User carpark relation for storing user selelcted carparks."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: Optional[int] = None
    UserId: str
    CarParkId: str
    PhoneParkingCode: str


class CarParkSelect(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    CarParkId: str
