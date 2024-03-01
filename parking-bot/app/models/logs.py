from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class ParkingOperationLogCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)
    PhoneParkingCode: str
    DeviceId: str
    LicensePlate: str
    Phone: str
    Type: Literal["start-sms", "stop-sms"]


class ParkingOperationLog(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: Optional[int] = None

    UserId: str
    PhoneParkingCode: str
    DeviceId: str
    LicensePlate: str
    Phone: str
    Type: Literal["start-sms", "stop-sms"]
    Timestamp: int
