import json
import logging

import httpx
import jwt
from cryptography.fernet import Fernet
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import conf
from app.services.log_manager import ParkingLogManager

from .models.user import User
from .services.carpark_data import CarParkDataSource
from .services.datastore import Database
from .services.user_manager import UserManager
from .services.userdata_manager import UserdataManager
from .util import http_error as err

__security = HTTPBearer(auto_error=True)  # raises forbidden/401 if no token
__ht_client = httpx.Client(http2=True)


def get_jwt(credentials: HTTPAuthorizationCredentials = Depends(__security)) -> dict:
    try:
        jwt_payload: dict = jwt.decode(
            jwt=credentials.credentials,
            key=conf.HS256_KEY,
            algorithms=["HS256"],
            verify=True,
        )
        return jwt_payload
    except Exception as ex:
        err.unauthorized(str(ex))


def __role_check(roles: list[str], *any_of) -> bool:
    for role in roles:
        if role in any_of:
            return True
    return False


def get_fernet(jwt: dict = Depends(get_jwt)) -> Fernet:
    try:
        jwt["sub"]
        return Fernet(key=jwt["sub"])
    except Exception as ex:
        err.bad_request(str(ex))


def get_cred_info() -> dict:
    try:
        with open(conf.CREDENTIALS_JSON, "rb") as f:
            return json.load(f)
    except Exception as ex:
        err.internal(str(ex))


def get_db(cred: dict = Depends(get_cred_info)) -> Database:
    try:
        db = Database(cred)
    except Exception as ex:
        logging.error(ex)
        err.internal("Could not initialize database api.")
    return db


def get_carpark_data() -> CarParkDataSource:
    try:
        return CarParkDataSource(conf, __ht_client)
    except Exception as ex:
        logging.error(ex)
        err.internal("Could not get open data service.")


def get_log_manager(
    db=Depends(get_db), fernet=Depends(get_fernet)
) -> ParkingLogManager:
    return ParkingLogManager(db, fernet)


def get_user_manager(db=Depends(get_db), fernet=Depends(get_fernet)) -> UserManager:
    return UserManager(db, fernet)


def get_userdata_manager(
    db: Database = Depends(get_db), fernet=Depends(get_fernet)
) -> UserdataManager:
    return UserdataManager(db, fernet)


def get_user(
    jwt: dict = Depends(get_jwt),
    um: UserManager = Depends(get_user_manager),
) -> User:
    try:
        # get user from token
        return um.get_user(jwt["sub"])
    except:
        pass
    err.unauthorized("User not found.")


def get_superuser(
    credentials: HTTPAuthorizationCredentials = Depends(__security),
    db: Database = Depends(get_db),
) -> User:
    user = get_user(credentials=credentials, db=db)
    if __role_check(user.Roles, "admin"):
        return user
    err.unauthorized("Privilege error.")
