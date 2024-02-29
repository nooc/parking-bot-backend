from typing import Optional

from pydantic import BaseModel, ConfigDict


class TollCarPark(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)
    Id: str
    Name: Optional[str] = None
    Owner: Optional[str] = None
    ParkingSpaces: Optional[int] = None
    PhoneParkingCode: Optional[str] = None
    ParkingCost: Optional[str] = None
    ParkingCharge: Optional[str] = None
    CurrentParkingCost: Optional[int] = None
    MaxParkingTime: Optional[str] = None
    MaxParkingTimeLimitation: Optional[str] = None
    Lat: Optional[float] = None
    Long: Optional[float] = None
    WKT: Optional[str] = None
