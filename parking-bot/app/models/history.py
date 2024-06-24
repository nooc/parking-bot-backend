from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict

type HistoryType = Literal["start-sms", "stop-sms", "start-kiosk"]


class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: Optional[int] = None

    UserId: Annotated[str, "index"]
    ParkingCode: str
    DeviceId: str
    LicensePlate: str
    Phone: str
    Type: HistoryType
    Start: int
    Stop: int


class HistoryItemCreate(BaseModel):
    ParkingCode: str
    DeviceId: str
    LicensePlate: str
    Type: HistoryType
    Start: int
    Stop: int
