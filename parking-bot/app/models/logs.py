from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class ParkingOperationLog(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: Optional[int] = None
    CarParkId: int
    UserId: str
    VehicleId: int
    Phone: str
    Type: Literal["start-sms", "stop-sms"]
    Timestamp: int
