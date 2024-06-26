from typing import Optional

from pydantic import BaseModel, ConfigDict


# external
class KioskParkingInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    externalId: str
    parkingAreaId: int
    maxTime: str

    name: Optional[str] = None
    heading: Optional[str] = None
    description: Optional[str] = None
    parkingFullDescription: Optional[str] = None
    parkingFullHeading: Optional[str] = None
    parkingName: Optional[str] = None
    availablePermitsCount: Optional[int] = 0


class KioskParkingCreate(BaseModel):
    Id: Optional[str] = None
    Lat: float
    Long: float


# internal
class KioskParkingInfoEx(KioskParkingInfo):
    Id: Optional[str] = None
    Lat: float
    Long: float
    CellId: str
    WKT: str


class KioskParkingRequest(BaseModel):
    externalId: str
    registrationNumber: str
    name: Optional[str] = ""
    phoneNumber: str
    setEndTimeReminder: Optional[bool] = True


class KioskParkingResponse(BaseModel):
    endTime: str  # 2023-12-31T16:19:13.8622192+01:00
    endTimeText: str  # 1 timme 59 minuter
    isLimited: bool  # false
    limitationText: Optional[str] = None
