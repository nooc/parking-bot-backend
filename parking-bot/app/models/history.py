from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict

type HistoryType = Literal[
    "create-user", "delete-user", "create-parking", "delete-parking"
]


class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: Optional[int] = None
    UserId: Annotated[str, "index"]
    Type: Annotated[HistoryType, "index"]
    Timestamp: Annotated[int, "index"]

    CarParkId: Annotated[Optional[str], "index"] = None
    VehicleId: Annotated[Optional[int], "index"] = None


__all__ = (
    "HistoryType",
    "HistoryItem",
)
