from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

type CarParkType = Literal["toll", "kiosk", "free"]


class CarPark(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    # db id
    Id: Optional[str] = None
    # dggs cell this location belongs to
    CellId: Annotated[str, "index"]

    Type: CarParkType

    # json for models.external.*.*ParkingInfo in bytes
    Info: str


__all__ = ("CarParkType", "CarPark")
