import httpx

from app.config import Settings
from app.models.external.kiosk import KioskParkingInfo
from app.services.datastore import Database


class KioskManager:

    _client: httpx.Client
    _url: str

    def __init__(self, db: Database, cfg: Settings, client: httpx.Client) -> None:
        self._db = db
        self._client = client
        self._url = cfg.GBG_PARKING_KIOSK_INFO_URL

    def get_kiosk_info(self, id: str) -> KioskParkingInfo:
        url = self._url.replace("{CLIENTID}", id)
        resp = self._client.get(url)
        resp.raise_for_status()
        return KioskParkingInfo(**resp.json())

    def get_checked(self, ids: list[str]) -> list[KioskParkingInfo]:
        to_remove: list[str] = []
        to_return: list[KioskParkingInfo] = []
        for id in ids:
            try:
                # get externalid and try fetch from kiosk service
                inf = self.get_kiosk_info(id)
                to_return.append(inf)
            except httpx.HTTPStatusError as ex:
                if ex.response.status_code == 404:
                    # only remove if not-found (other error requests ar not not-found)
                    to_remove.append(id)
        if to_remove:
            self._db.delete_objects([("Kiosk", i) for i in to_remove])
        return to_return
