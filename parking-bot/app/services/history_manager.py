from typing import List

from app.models.history import HistoryItem, HistoryType
from app.models.user import User
from app.services.data_manager import _DataManager


class ParkingHistoryManager(_DataManager):

    def __init__(self, db, fernet):
        super().__init__(db, fernet, ["LicensePlate", "Phone"])

    def log(
        self,
        user: User,
        ParkingCode: str,
        DeviceId: str,
        LicensePlate: str,
        Type: HistoryType,
        Start: int,
        Stop: int,
    ) -> HistoryItem:
        log_data = dict(
            UserId=user.Id,
            ParkingCode=ParkingCode,
            DeviceId=DeviceId,
            LicensePlate=LicensePlate,
            Phone=user.Phone,
            Type=Type,
            Start=Start,
            Stop=Stop,
        )
        log_data = self._shade(log_data)
        log = HistoryItem(**log_data)
        self._db.put_object(log)
        return log

    def list(self, user: User, **kwargs) -> List[HistoryItem]:
        filters = [("UserId", "=", user.Id)]
        args = {}
        if "from_time" in kwargs:
            filters.append(("Timestamp", ">=", kwargs["from_time"]))
        if "offset" in kwargs:
            args["offset"] = kwargs["offset"]
        if "limit" in kwargs:
            args["limit"] = kwargs["limit"]
        ret = self._db.get_objects_by_query(
            HistoryItem, filters=filters, order=["Stop"], **args
        )
        return [HistoryItem(**self._unshade(log_item)) for log_item in ret]


__all__ = ("ParkingHistoryManager",)
