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


# internal
class KioskParkingInfoEx(KioskParkingInfo):
    Id: Optional[str] = None
    Lat: float
    Long: float
    CellId: str
    WKT: str
