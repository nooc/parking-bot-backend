from typing import List

from app.models.logs import ParkingOperationLog, ParkingOperationType
from app.models.user import User
from app.services.data_manager import _DataManager
from app.util.time import get_utc_millis


class ParkingLogManager(_DataManager):

    def __init__(self, db, fernet):
        super().__init__(db, fernet, ["LicensePlate", "Phone"])

    def log(
        self,
        user: User,
        ParkingCode: str,
        DeviceId: str,
        LicensePlate: str,
        Type: ParkingOperationType,
    ) -> None:
        log_data = dict(
            UserId=user.Id,
            ParkingCode=ParkingCode,
            DeviceId=DeviceId,
            LicensePlate=LicensePlate,
            Phone=user.Phone,
            Type=Type,
            Timestamp=get_utc_millis(),
        )
        log_data = self._shade(log_data)
        self._db.put_object(ParkingOperationLog(**log_data))

    def list(self, user: User, **kwargs) -> List[ParkingOperationLog]:
        filters = [("UserId", "=", user.Id)]
        args = {}
        if "from_time" in kwargs:
            filters.append(("Timestamp", ">=", kwargs["from_time"]))
        if "offset" in kwargs:
            args["offset"] = kwargs["offset"]
        if "limit" in kwargs:
            args["limit"] = kwargs["limit"]
        ret = self._db.get_objects_by_query(
            ParkingOperationLog, filters=filters, order=["Timestamp"], **args
        )
        return [ParkingOperationLog(**self._unshade(log_item)) for log_item in ret]
