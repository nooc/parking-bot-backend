from typing import Optional

from pydantic import BaseModel, ConfigDict


class FreeParkingInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: str
    Lat: float
    Long: float

    Name: Optional[str] = None
    Owner: Optional[str] = None
    ParkingSpaces: Optional[int] = 0
    MaxParkingTime: Optional[str] = None
    MaxParkingTimeLimitation: Optional[str] = None
    ExtraInfo: Optional[str] = None
    Distance: Optional[int] = 0
    WKT: Optional[str] = None
