from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

type CarParkType = Literal["toll", "kiosk", "free"]


class CarPark(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    # db id
    Id: Optional[str] = None
    # dggs cell this location belongs to
    CellId: str

    Type: CarParkType

    # json for models.external.*.*ParkingInfo
    Info: str


__all__ = ("CarParkType", "CarPark")
