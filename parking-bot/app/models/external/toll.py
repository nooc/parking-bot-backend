from typing import Optional

from pydantic import BaseModel, ConfigDict


class TollParkingInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: str
    PhoneParkingCode: str
    Lat: float
    Long: float

    Name: Optional[str] = None
    Owner: Optional[str] = None
    ParkingSpaces: Optional[int] = None
    ParkingCost: Optional[str] = None
    ParkingCharge: Optional[str] = None
    CurrentParkingCost: Optional[int] = None
    MaxParkingTime: Optional[str] = None
    MaxParkingTimeLimitation: Optional[str] = None
    WKT: Optional[str] = None
