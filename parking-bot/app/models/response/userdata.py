from pydantic import BaseModel, ConfigDict

from app.models.user import User
from app.models.vehicle import Vehicle


class UserData(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    User: User
    Vehicles: list[Vehicle]


__all__ = ("UserData",)
