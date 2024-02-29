from typing import Optional

from pydantic import BaseModel


class FreeCarPark(BaseModel):
    Id: str
    Name: Optional[str] = None
    Owner: Optional[str] = None
    ParkingSpaces: Optional[int] = None
    MaxParkingTime: Optional[str] = None
    MaxParkingTimeLimitation: Optional[str] = None
    ExtraInfo: Optional[str] = None
    Distance: Optional[int] = None
    Lat: Optional[float] = None
    Long: Optional[float] = None
    WKT: Optional[str] = None
