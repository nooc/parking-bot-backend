from datetime import datetime

from pydantic import BaseModel


class CellInfo(BaseModel):
    Id: str
    Expires: int
