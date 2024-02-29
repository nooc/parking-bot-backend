import httpx

from app.config import Settings


class KioskParking:
    """Open parking data"""

    __client: httpx.Client
    __kiosk_info: str

    def __init__(self, conf: Settings, client: httpx.Client):
        self.__client = client
        self.__kiosk_info = conf.GBG_PARKING_KIOSK_INFO_URL
