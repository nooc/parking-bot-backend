from enum import IntEnum
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict

type RoleType = Literal["user", "admin"]


class UserState(IntEnum):
    Normal = 0
    Disabled = 1


# Create params
class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: str
    Phone: str


# Update params
class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Phone: Optional[str] = None


# Db object
class User(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    Id: str
    State: UserState
    Phone: str
    Roles: List[RoleType]
