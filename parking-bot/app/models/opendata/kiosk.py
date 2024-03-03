from pydantic import BaseModel


class KioskInfo(BaseModel):
    externalId: str
    name: str
    heading: str
    description: str
    parkingFullDescription: str
    parkingFullHeading: str
    parkingName: str
    parkingAreaId: int
    availablePermitsCount: int
    maxTime: str
