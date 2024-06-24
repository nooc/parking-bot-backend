from enum import IntEnum
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict

type RoleType = Literal["user", "admin"]


class UserState(IntEnum):
    Normal = 0
    Disabled = 1


# Update params
class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Phone: Optional[str] = None
    CarParks: Optional[list[str]] = None
    Roles: Optional[list[RoleType]] = None
    State: Optional[UserState] = None


# Db object
class User(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: str
    State: Annotated[UserState, "index"]
    Phone: Optional[str] = None
    Roles: list[RoleType]
    CarParks: Optional[list[str]] = []


__all__ = ("RoleType", "UserState", "UserUpdate", "User")
