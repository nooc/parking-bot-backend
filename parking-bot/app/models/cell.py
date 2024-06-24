from datetime import datetime
from typing import Annotated

from pydantic import BaseModel


class CellInfo(BaseModel):
    Id: str
    Expires: Annotated[int, "index"]


__all__ = ("CellInfo",)
