from typing import Optional

from pydantic import BaseModel

from app.models.carpark import CarParkType


# TODO: Do we need this?
class ParkingRequest(BaseModel):
    # CarPark id
    Id: str


class ActiveParking(BaseModel):
    Id: Optional[int] = None
    CarParkId: str
    UserId: str

    Type: CarParkType
    Start: int
    Stop: int


__all__ = ("ParkingRequest", "ActiveParking")
