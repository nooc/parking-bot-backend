import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
import jwt.utils
from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import PlainTextResponse

import app.util.http_error as err
from app.config import conf
from app.dependencies import (
    get_db,
    get_jwt,
    get_user,
    get_user_manager,
    get_vehicle_manager,
)
from app.endpoints.media_types import MEDIA_TYPE_JSON
from app.models.carpark import *
from app.models.response.userdata import UserData
from app.models.user import User, UserUpdate
from app.models.vehicle import Vehicle
from app.services.user_manager import UserManager
from app.services.vehicle_manager import VehicleManager

router = APIRouter()

__IDENTIFIER = "identifier"


@router.get("", status_code=status.HTTP_200_OK)
def get_user(current_user: User = Depends(get_user)) -> User:
    return current_user


@router.post(
    "/init",
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK,
    response_description=f"A JWT access token valid for {conf.JWT_EXP_DAYS} days.",
    description="""Initialize or refresh a user. If a user does not exist, it is created.
    On success, will return an access token for the API.

    This method requires a signed bearer token with issuer and a 'identifier' claim.""",
)
def init_user(
    um: UserManager = Depends(get_user_manager),
    jwtd: dict = Depends(get_jwt),
) -> str:
    if not __IDENTIFIER in jwtd:
        err.bad_request("No identifier")
    # android secure device id is 64bit hex string
    try:
        int(jwtd[__IDENTIFIER], 16)
    except:
        err.bad_request("Invalid identifier")
    try:
        user = um.get_user(jwtd[__IDENTIFIER])
    except:
        user = None
    if not user:
        logging.info('Creating user "%s"', jwtd[__IDENTIFIER])
        user = um.create_user(id=jwtd[__IDENTIFIER])
    if not user:
        err.internal("Could not create user.")
    dt = datetime.now(UTC)
    return jwt.encode(
        payload={
            "sub": user.Id,
            "exp": dt + timedelta(days=conf.JWT_EXP_DAYS),
            "iss": conf.JWT_ISSUER,
            "iat": dt,
            "aud": conf.JWT_AUDIENCE,
        },
        key=conf.HS256_KEY,
        algorithm="HS256",
    )


@router.put("", status_code=status.HTTP_200_OK)
def update_user(
    um: UserManager = Depends(get_user_manager),
    current_user: User = Depends(get_user),
    user_data: UserUpdate = Body(title="Data to update", media_type=MEDIA_TYPE_JSON),
) -> User:
    needs_admin = user_data.model_fields_set.intersection(set(["State", "Roles"]))
    if len(needs_admin) != 0 and not "admin" in current_user.Roles:
        err.forbidden("Not enough privileges")
    return um.update_user(user=current_user, **user_data.model_dump(exclude_unset=True))


@router.delete("", status_code=status.HTTP_200_OK)
def delete_user(
    um: UserManager = Depends(get_user_manager),
    current_user: User = Depends(get_user),
) -> Any:
    um.delete_user(user_id=current_user.Id)


@router.get("/data", status_code=status.HTTP_200_OK)
def get_settings(
    um: UserManager = Depends(get_user_manager),
    vm: VehicleManager = Depends(get_vehicle_manager),
    current_user: User = Depends(get_user),
) -> UserData:
    try:
        vehicles = vm.list_vehicles(user=current_user)
        return UserData(
            User=current_user,
            Vehicles=[Vehicle(**v.model_dump()) for v in vehicles],
        )
    except Exception as ex:
        err.internal(str(ex))
