import enum
import logging
from typing import Literal

import httpx

import app.util.http_error as err
from app.config import Settings
from app.models.carpark import CarPark
from app.models.external.kiosk import (
    KioskParkingInfo,
    KioskParkingInfoEx,
    KioskParkingRequest,
    KioskParkingResponse,
)
from app.models.user import User
from app.models.vehicle import VehicleDb
from app.services.datastore import Database
from app.util.carpark_id import CarParkId
from app.util.dggs import Dggs


class AssignmentResponse(enum.IntEnum):
    OK = 0
    FULL = 1
    UNAVAILABLE = 2


class KioskManager:

    __GET_INFO = "?externalId={CLIENTID}"
    __POST_ASSIGNMENT = "/assignment"

    _client: httpx.Client
    _base_url: str

    def __init__(
        self, db: Database, cfg: Settings, client: httpx.Client, dggs: Dggs
    ) -> None:
        self._db = db
        self._client = client
        self._base_url = cfg.GBG_PARKING_KIOSK_BASE_URL
        self._dggs = dggs

    def get_kiosk_info(self, id: str) -> KioskParkingInfo:
        """Get `KioskParkingInfo` by kiosk client id.

        Args:
            id (str): kiosk client id

        Returns:
            KioskParkingInfo: Parking information
        Raises:
            HttpStatusError on 400+
        """
        url = f"{self._base_url}{self.__GET_INFO}".replace("{CLIENTID}", id)
        resp = self._client.get(url)
        resp.raise_for_status()
        return KioskParkingInfo(**resp.json())

    def validate_kiosks(self) -> None:
        """Remove invalid ids from db."""
        kiosks: list[KioskParkingInfoEx] = self._db.get_objects(KioskParkingInfoEx)
        for kiosk in kiosks:
            try:
                # get externalid and try fetch from kiosk service
                inf = self.get_kiosk_info(kiosk.Id)
            except httpx.HTTPStatusError as ex:
                self._db.delete_object(kiosk)

    def try_add_to_known_kiosks(self, id: str, lat: float, lon: float) -> None:
        """Try adding kiosk client to known kiosks.

        Args:
            id (str): kiosk client id
        Raises:
            httpx.HTTPStatusError(404)
        """
        result = self._db.get_object(KioskParkingInfoEx, id)
        if result:
            return
        try:
            info = self.get_kiosk_info(id)
            if info:
                cell = self._dggs.lat_lon_to_cells(
                    lat=lat, lon=lon, include_neighbors=False
                )[0]
                kiosk = KioskParkingInfoEx(
                    Id=id, Lat=lat, Long=lon, CellId=cell, **info.model_dump()
                )
                self._db.put_object(kiosk)
        except Exception as ex:
            logging.warning(str(ex))

    def update_kiosks(self, id: str, lat: float, lon: float) -> None:
        """Update known kiosk info by setting provided lat/lon and refreshing info from source.

        Args:
            id (str): kiosk client id
        Raises:
            httpx.HTTPStatusError(404)
        """
        item: KioskParkingInfoEx = self._db.get_object(KioskParkingInfoEx, id)
        if item:
            try:
                info = self.get_kiosk_info(id)
                if info:
                    item.CellId = self._dggs.lat_lon_to_cells(
                        lat=lat, lon=lon, include_neighbors=False
                    )[0]
                    item.Lat = lat
                    item.Long = lon
                    self._db.put_object(item)
                    self.__update_carpark(item)
            except Exception as ex:
                logging.warning(str(ex))
        else:
            err.not_found(f"Kiosk not found: {id}")

    def __update_carpark(self, kiosk: KioskParkingInfoEx) -> None:
        """Update CarPark containing the kiosk info.

        Args:
            kiosk (KioskParkingInfoEx): Updated kiosk info.
        """
        carpark_id = CarParkId.kiosk_id(kiosk)
        item: CarPark = self._db.get_object(CarPark, carpark_id)
        if item:
            item.CellId = kiosk.CellId
            item.Info = kiosk.model_dump_json()
            self._db.put_object(item)

    def try_park(
        self,
        user: User,
        kiosk: KioskParkingInfoEx,
        vehicle: VehicleDb,
    ) -> tuple[AssignmentResponse, KioskParkingResponse]:
        url = f"{self._base_url}{self.__POST_ASSIGNMENT}"
        body = KioskParkingRequest(
            externalId=kiosk.externalId,
            registrationNumber=vehicle.LicensePlate,
            phoneNumber=user.Phone,
            setEndTimeReminder=user.Reminders,
        )
        resp = self._client.post(url, json=body)  # TODO: can we set json to BaseModel?
        match resp.status_code:
            case 424:
                return AssignmentResponse.UNAVAILABLE, None
            case 0:  # TODO: find out response code when full
                return AssignmentResponse.FULL, None
            case 200:
                return AssignmentResponse.OK, KioskParkingResponse.model_validate_json(
                    resp.content
                )
            case _:
                err.internal(f"Unexpected response from kiosk: {resp.status_code}")


__all__ = ("KioskManager", "AssignmentResponse")
