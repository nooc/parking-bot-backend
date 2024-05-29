from urllib.parse import quote

import httpx
from httpx import Client

from app.config import Settings
from app.models.opendata.free import FreeCarPark
from app.models.opendata.kiosk import KioskInfo
from app.models.opendata.toll import TollCarPark


class CarParkDataSource:
    """Open parking data"""

    __client: Client
    __app_id: str
    __base_url: str
    __toll_list: str
    __toll_item: str
    __free_list: str
    __free_item: str

    def __init__(self, conf: Settings, client: httpx.Client):
        self.__app_id = conf.GBG_DATA_APP_ID
        self.__base_url = conf.GBG_DATA_BASE_URL
        self.__toll_list = conf.GBG_DATA_TOLL_LIST
        self.__toll_item = conf.GBG_DATA_TOLL_ITEM
        self.__free_list = conf.GBG_DATA_FREE_LIST
        self.__free_item = conf.GBG_DATA_FREE_ITEM
        self.__kiosk = conf.GBG_PARKING_KIOSK_INFO_URL
        self.__client = client

    def _replace(self, tpl_url, **items) -> str:
        url = tpl_url
        for k, v in items.items():
            kk = "{" + k + "}"
            if kk in url:
                if k == "ID":
                    url = url.replace(kk, v)
                else:
                    url = url.replace(kk, quote(v))
        return url

    def get_appid(self) -> str:
        return self.__app_id

    def get_nearby_toll_parking(
        self, lat: float, lon: float, radius: int
    ) -> list[TollCarPark]:
        part_url = self._replace(
            self.__toll_list,
            APPID=self.__app_id,
            LATITUDE=str(lat),
            LONGITUDE=str(lon),
            RADIUS=str(radius),
        )
        resp = self.__client.get(f"{self.__base_url}{part_url}").json()
        return [TollCarPark(**d) for d in resp]

    def get_toll_parking(self, id: str) -> TollCarPark:
        part_url = self._replace(self.__toll_item, APPID=self.__app_id, ID=id)
        resp = self.__client.get(f"{self.__base_url}{part_url}").json()
        return TollCarPark(**resp)

    def get_nearby_free_parking(
        self, lat: float, lon: float, radius: int
    ) -> list[FreeCarPark]:
        part_url = self._replace(
            self.__free_list,
            APPID=self.__app_id,
            LATITUDE=str(lat),
            LONGITUDE=str(lon),
            RADIUS=str(radius),
        )
        resp = self.__client.get(f"{self.__base_url}{part_url}").json()
        return [FreeCarPark(**d) for d in resp]

    def get_free_parking(self, id: str) -> FreeCarPark:
        part_url = self._replace(self.__free_item, APPID=self.__app_id, ID=id)
        resp = self.__client.get(f"{self.__base_url}{part_url}").json()
        return FreeCarPark(**resp)

    def get_kiosk_info(self, id: str) -> KioskInfo:
        url = self._replace(self.__kiosk, CLIENTID=id)
        resp = self.__client.get(url).json()
        return KioskInfo(**resp)


__all__ = ("CarParkDataSource",)
