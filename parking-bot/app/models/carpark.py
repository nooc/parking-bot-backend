from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class CarPark(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    # db id
    Id: Optional[int] = None
    # dggs cell this location belongs to
    CellId: str

    Type: Literal["toll", "kiosk", "free"]

    # json for models.external.*.*ParkingInfo
    Info: str


class SelectedCarParks(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Toll: Optional[list[int]] = []
    Kiosk: Optional[list[int]] = []
    Free: Optional[list[int]] = []


class Kiosk(BaseModel):
    Id: str
    CellId: str
