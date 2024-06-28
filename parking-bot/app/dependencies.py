import base64
import hashlib
import json
import logging
import os

import httpx
import jwt
from cryptography.fernet import Fernet
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.cloud.tasks_v2 import CloudTasksClient

from app.config import conf

from .models.user import User
from .util import http_error as err
from .util.dggs import Dggs

__auth_err = "FAKE_AUTH" not in os.environ  # TODO: remove fake auth override
__security = HTTPBearer(auto_error=__auth_err)  # raises forbidden/401 if no token
__ht_client = httpx.Client(http2=True)


def get_cloud_tasks() -> CloudTasksClient:
    return CloudTasksClient()


def get_jwt(credentials: HTTPAuthorizationCredentials = Depends(__security)) -> dict:
    # TODO: remove fake auth override
    if "FAKE_AUTH" in os.environ:
        return {"sub": "0a0a0a0a0a0a0a01", "identifier": "0a0a0a0a0a0a0a01"}
    try:
        jwt_payload: dict = jwt.decode(
            jwt=credentials.credentials,
            key=conf.HS256_KEY,
            algorithms=["HS256"],
            issuer=conf.JWT_ISSUER,
            verify=True,
            audience=conf.JWT_AUDIENCE,
        )
        if "sub" in jwt_payload or "identifier" in jwt_payload:
            return jwt_payload
        msg = "Invalid claims"
    except Exception as ex:
        msg = str(ex)
        logging.warn(msg)

    err.unauthorized(msg)


def __role_check(roles: list[str], *any_of) -> bool:
    for role in roles:
        if role in any_of:
            return True
    return False


def __to_fernet_key(source: str) -> bytes:
    h = hashlib.new("sha256")
    h.update(source.encode())
    return base64.urlsafe_b64encode(h.digest())


def get_fernet(jwt: dict = Depends(get_jwt)) -> Fernet:
    try:
        if "sub" in jwt:
            key = __to_fernet_key(jwt["sub"])
        elif "identifier" in jwt:
            key = __to_fernet_key(jwt["identifier"])
        else:
            err.bad_request("missing identity")
        return Fernet(key=key)
    except Exception as ex:
        err.bad_request(str(ex))


def get_cred_info() -> dict:
    try:
        with open(conf.CREDENTIALS_JSON, "rb") as f:
            return json.load(f)
    except Exception as ex:
        err.internal(str(ex))


from app.services.datastore import Database


def get_db(cred: dict = Depends(get_cred_info)) -> Database:
    try:
        db = Database(cred)
    except Exception as ex:
        logging.error(ex)
        err.internal("Could not initialize database api.")
    return db


from app.services.history_manager import HistoryManager


def get_history_manager(db=Depends(get_db)) -> HistoryManager:
    return HistoryManager(db=db)


from app.services.gothenburg_open_data import CarParkDataSource


def get_carpark_data() -> CarParkDataSource:
    try:
        return CarParkDataSource(conf, __ht_client)
    except Exception as ex:
        logging.error(ex)
        err.internal("Could not get open data service.")


from app.services.history_manager import HistoryManager


def get_log_manager(db=Depends(get_db), fernet=Depends(get_fernet)) -> HistoryManager:
    return HistoryManager(db, fernet)


from app.services.user_manager import UserManager


def get_user_manager(db=Depends(get_db), fernet=Depends(get_fernet)) -> UserManager:
    return UserManager(db, fernet)


from app.services.vehicle_manager import VehicleManager


def get_vehicle_manager(
    db: Database = Depends(get_db), fernet=Depends(get_fernet)
) -> VehicleManager:
    return VehicleManager(db, fernet)


def get_user(
    jwt: dict = Depends(get_jwt),
    um: UserManager = Depends(get_user_manager),
) -> User:
    try:
        # get user from token
        return um.get_user(jwt["sub"])
    except Exception as ex:
        err.not_found(str(ex))


def get_superuser(
    credentials: HTTPAuthorizationCredentials = Depends(__security),
    db: Database = Depends(get_db),
) -> User:
    user = get_user(credentials=credentials, db=db)
    if __role_check(user.Roles, "admin"):
        return user
    err.unauthorized("Privilege error.")


def get_dggs() -> Dggs:
    return Dggs()


from app.services.kiosk_manager import KioskManager


def get_kiosk_manager(
    db: Database = Depends(get_db),
    dggs: Database = Depends(get_dggs),
) -> KioskManager:
    return KioskManager(db=db, cfg=conf, client=__ht_client, dggs=dggs)


from app.services.carpark_manager import CarParkManager


def get_carpark_manager(
    db: Database = Depends(get_db),
    source: CarParkDataSource = Depends(get_carpark_data),
    dggs: Database = Depends(get_dggs),
    kiosk: KioskManager = Depends(get_kiosk_manager),
) -> CarParkManager:
    return CarParkManager(db=db, source=source, dggs=dggs, cfg=conf, kiosk=kiosk)


from app.services.parking_manager import ParkingManager


def get_parking_manager(
    db: Database = Depends(get_db),
    carparks: CarParkManager = Depends(get_carpark_manager),
    vehicles: VehicleManager = Depends(get_vehicle_manager),
    history: HistoryManager = Depends(get_history_manager),
    kiosk: KioskManager = Depends(get_kiosk_manager),
) -> ParkingManager:
    return ParkingManager(
        db=db,
        cfg=conf,
        client=__ht_client,
        carparks=carparks,
        vehicles=vehicles,
        history=history,
        kiosk=kiosk,
    )


from app.services.task_manager import TaskManager


def get_task_manager(
    db: Database = Depends(get_db),
    client=Depends(get_cloud_tasks),
    parking: ParkingManager = Depends(get_parking_manager),
) -> TaskManager:
    return TaskManager(db=db, client=client, parking=parking, cfg=conf)
