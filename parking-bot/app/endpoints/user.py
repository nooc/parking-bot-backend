import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
import jwt.utils
from fastapi import APIRouter, Body, Depends, Query, status
from fastapi.responses import PlainTextResponse

import app.util.http_error as err
from app.config import conf
from app.dependencies import (
    get_db,
    get_jwt,
    get_user,
    get_user_manager,
    get_userdata_manager,
)
from app.endpoints.media_types import MEDIA_TYPE_JSON
from app.models.carpark import *
from app.models.response.userdata import UserData
from app.models.user import User, UserUpdate
from app.models.vehicle import Vehicle, VehicleDb
from app.services.datastore import Database
from app.services.user_manager import UserManager
from app.services.userdata_manager import UserdataManager

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
    id_ok = False
    # android secure device id is 64bit hex string
    try:
        int(jwtd[__IDENTIFIER], 16)
        id_ok = True
    except:
        pass
    # ios
    # try:
    # ...
    #    id_ok = True
    # except: pass
    if not id_ok:
        err.bad_request()
    try:
        user = um.get_user(jwtd[__IDENTIFIER])
    except:
        user = None
    if not user:
        logging.info('Creating user "%s"', jwtd[__IDENTIFIER])
        user = um.create_user(Id=jwtd[__IDENTIFIER])
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
    return um.update_user(user=current_user, **user_data.model_dump(exclude_unset=True))


@router.delete("", status_code=status.HTTP_200_OK)
def delete_user(
    um: UserManager = Depends(get_user_manager),
    current_user: User = Depends(get_user),
) -> Any:
    um.delete_user(current_user)


@router.get("/data", status_code=status.HTTP_200_OK)
def get_settings(
    udata: UserdataManager = Depends(get_userdata_manager),
    current_user: User = Depends(get_user),
) -> UserData:
    try:
        vehicles = udata.list_vehicles(current_user)
        tolls = udata.list_toll_carparks(current_user)
        kiosks = udata.list_kiosk_carparks(current_user)
        return UserData(
            User=current_user,
            Vehicles=[Vehicle(**v.model_dump()) for v in vehicles],
            CarParks=CarParks(
                Toll=[SelectedTollPark(**t.model_dump()) for t in tolls],
                Kiosk=[SelectedKioskPark(**k.model_dump()) for k in kiosks],
            ),
        )
    except Exception as ex:
        err.internal(str(ex))
