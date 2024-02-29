from typing import Optional

from pydantic import BaseModel, ConfigDict


class Vehicle(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: Optional[int] = None
    UserId: str
    LicensePlate: str
    Name: str
