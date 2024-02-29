from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.carpark import SelectedCarPark
from app.models.user import User
from app.models.vehicle import Vehicle


class UserData(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    User: User
    Vehicles: list[Vehicle]
    CarParks: list[SelectedCarPark]
