from typing import Any

from fastapi import APIRouter, Body, Depends, status

import app.endpoints.media_types as mtype
import app.util.http_error as err
from app.dependencies import get_db, get_jwt, get_user, get_user_manager
from app.models.carpark import SelectedCarPark
from app.models.response.userdata import UserData
from app.models.user import User, UserRegister, UserUpdate
from app.models.vehicle import Vehicle
from app.services.datastore import Database
from app.services.user_manager import UserManager

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
def get_user(current_user: User = Depends(get_user)) -> User:
    return current_user


@router.post("/register", status_code=status.HTTP_200_OK)
def register_user(
    um: UserManager = Depends(get_user_manager),
    jwt: dict = Depends(get_jwt),
    user_data: UserRegister = Body(
        title="Registration data", media_type=mtype.MEDIA_TYPE_REGISTER_USER
    ),
) -> User:
    # TODO Validate jwt against 3rd party.
    # ...
    return um.create_user(Id=jwt["sub"], **user_data.model_dump())


@router.put("", status_code=status.HTTP_200_OK)
def update_user(
    um: UserManager = Depends(get_user_manager),
    current_user: User = Depends(get_user),
    user_data: UserUpdate = Body(
        title="User update data", media_type=mtype.MEDIA_TYPE_UPDATE_USER
    ),
) -> User:
    return um.update_user(user=current_user, **user_data.model_dump(exclude_unset=True))


@router.delete("", status_code=status.HTTP_200_OK)
def delete_user(
    um: UserManager = Depends(get_user_manager),
    current_user: User = Depends(get_user),
) -> Any:
    um.delete_user(current_user)


@router.get("/data", status_code=status.HTTP_200_OK)
def get_settings(
    db: Database = Depends(get_db), current_user: User = Depends(get_user)
) -> UserData:
    try:
        vehicles = db.get_objects_by_query(
            Vehicle, filters=[("UserId", "=", current_user.Id)]
        )
        car_parks = db.get_objects_by_query(
            SelectedCarPark, filters=[("UserId", "=", current_user.Id)]
        )
        return UserData(User=current_user, Vehicles=vehicles, CarParks=car_parks)
    except:
        err.internal("Error getting settings.")
