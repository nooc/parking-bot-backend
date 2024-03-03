import base64
import json
import logging

import httpx
import jwt
from cryptography.fernet import Fernet
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import conf
from app.services.kiosk_parking import KioskParking

from .models.user import User
from .services.datastore import Database
from .services.open_data_parking import OpenDataParking
from .services.user_manager import UserManager
from .services.userdata_manager import UserdataManager
from .util import http_error as err

__security = HTTPBearer(auto_error=True)  # raises forbidden/401 if no token
__ht_client = httpx.Client(http2=True)


def __role_check(roles: list[str], *any_of) -> bool:
    for role in roles:
        if role in any_of:
            return True
    return False


def get_fernet() -> Fernet:
    return Fernet(key=conf.FERNET_KEY)


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


def get_open_data_service() -> OpenDataParking:
    try:
        return OpenDataParking(conf, __ht_client)
    except Exception as ex:
        logging.error(ex)
        err.internal("Could not get open data service.")


def get_kiosk_service() -> KioskParking:
    return KioskParking(conf, __ht_client)


def get_user_manager(db=Depends(get_db), fernet=Depends(get_fernet)) -> UserManager:
    return UserManager(db, fernet)


def get_userdata_manager(
    db: Database = Depends(get_db), fernet=Depends(get_fernet)
) -> UserdataManager:
    return UserdataManager(db, fernet)


def get_jwt(credentials: HTTPAuthorizationCredentials = Depends(__security)) -> dict:
    try:
        bkey = "some key"
        jwt_payload: dict = jwt.decode(
            jwt=credentials.credentials,
            key=bkey,
            algorithms=["HS256"],
            verify=True,
        )
        return jwt_payload
    except Exception as ex:
        err.unauthorized("Bad token.")


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
