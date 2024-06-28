from typing import Annotated, Optional

from pydantic import BaseModel

from app.models.carpark import CarParkType


class ParkingRequest(BaseModel):
    # CarPark id
    CarParkId: str
    VehicleId: int


class ActiveParking(BaseModel):
    Id: Optional[int] = None
    CarParkId: Annotated[str, "index"]
    UserId: Annotated[str, "index"]
    VehicleId: Annotated[int, "index"]
    Type: Annotated[CarParkType, "index"]
    Timestamp: Annotated[Optional[int], "index"] = None


__all__ = ("ParkingRequest", "ActiveParking")
