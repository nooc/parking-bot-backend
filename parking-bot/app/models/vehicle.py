from typing import Optional

from pydantic import BaseModel, ConfigDict


class VehicleAdd(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)
    DeviceId: str
    LicensePlate: str
    Name: str


class Vehicle(VehicleAdd):
    Id: Optional[int] = None


class VehicleDb(Vehicle):
    Id: Optional[int] = None
    UserId: str


class VehicleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Name: Optional[str] = None
