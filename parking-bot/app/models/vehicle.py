from typing import Optional

from pydantic import BaseModel, ConfigDict


class Vehicle(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: Optional[int] = None
    UserId: str
    DeviceId: str
    LicensePlate: str
    Name: str


class VehicleCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    DeviceId: str
    LicensePlate: str
    Name: str


class VehicleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    DeviceId: Optional[str] = None
    LicensePlate: Optional[str] = None
    Name: Optional[str] = None
