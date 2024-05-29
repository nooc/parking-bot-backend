from datetime import UTC, datetime, timedelta
from typing import Any, AnyStr

import jwt
import jwt.utils
from fastapi import APIRouter, Body, Depends, Query, status
from fastapi.responses import PlainTextResponse

import app.util.http_error as err
from app.config import conf
from app.dependencies import get_db, get_jwt, get_user, get_user_manager
from app.endpoints.media_types import MEDIA_TYPE_JSON
from app.models.carpark import *
from app.models.response.userdata import UserData
from app.models.user import User, UserUpdate
from app.models.vehicle import Vehicle, VehicleDb
from app.services.datastore import Database
from app.services.user_manager import UserManager

router = APIRouter()


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
    if not "identifier" in jwtd:
        err.bad_request("No identifier")
    id_ok = False
    # android secure device id is 64bit hex string
    try:
        int(jwtd["identifier"], 16)
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
        user = um.get_user(jwtd["identifier"])
    except:
        user = None
    if not user:
        user = um.create_user(Id=jwtd["identifier"])
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
    db: Database = Depends(get_db), current_user: User = Depends(get_user)
) -> UserData:
    try:
        vehicles = db.get_objects_by_query(
            VehicleDb, filters=[("UserId", "=", current_user.Id)]
        )
        toll = db.get_objects_by_query(
            SelectedTollParkDb, filters=[("UserId", "=", current_user.Id)]
        )
        kiosk = db.get_objects_by_query(
            SelectedKioskParkDb, filters=[("UserId", "=", current_user.Id)]
        )
        return UserData(
            User=current_user,
            Vehicles=vehicles,
            SelectedParking=CarParks(
                Toll=[SelectedTollPark(**t.model_dump()) for t in toll],
                Kiosk=[SelectedKioskPark(**k.model_dump()) for k in kiosk],
            ),
        )
    except:
        err.internal("Error getting settings.")
