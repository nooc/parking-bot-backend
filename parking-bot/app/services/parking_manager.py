from typing import Union

import firebase_admin
import httpx
from firebase_admin import App as FirebaseApp
from firebase_admin import messaging

import app.util.http_error as err
from app.config import Settings
from app.models.user import User
from app.services.datastore import Database


class ParkingManager:

    _fb_app: FirebaseApp

    def __init__(
        self, cred: Union[dict, str], db: Database, cfg: Settings, http: httpx.Client
    ) -> None:
        self._db = db
        self._cfg = cfg
        self._http = http

        self._fb_app = firebase_admin.initialize_app()

    def request(self, user: User, carpark_id: str) -> None:
        err.internal(f"Not implemented: {__name__}")

    def delete(self, user: User, parking_id: str) -> None:
        # messaging.Message()
        err.internal(f"Not implemented: {__name__}")
