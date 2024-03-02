from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

type ParkingOperationType = Literal["start-sms", "stop-sms"]


class ParkingOperationLog(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: Optional[int] = None

    UserId: str
    PhoneParkingCode: str
    DeviceId: str
    LicensePlate: str
    Phone: str
    Type: ParkingOperationType
    Timestamp: int
