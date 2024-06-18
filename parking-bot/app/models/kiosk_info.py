from pydantic import BaseModel


class KioskInfo(BaseModel):
    ExternalId: str
    Name: str
    Heading: str
    Description: str
    ParkingFullDescription: str
    ParkingFullHeading: str
    ParkingName: str
    ParkingAreaId: int
    AvailablePermitsCount: int
    MaxTime: str
