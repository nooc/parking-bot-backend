import logging

import httpx

import app.util.http_error as err
from app.config import Settings
from app.models.carpark import CarPark
from app.models.external.kiosk import KioskParkingInfo, KioskParkingInfoEx
from app.services.datastore import Database
from app.util.carpark_id import CarParkId
from app.util.dggs import Dggs


class KioskManager:

    _client: httpx.Client
    _url: str

    def __init__(
        self, db: Database, cfg: Settings, client: httpx.Client, dggs: Dggs
    ) -> None:
        self._db = db
        self._client = client
        self._url = cfg.GBG_PARKING_KIOSK_INFO_URL
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
        url = self._url.replace("{CLIENTID}", id)
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
