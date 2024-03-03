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
        PhoneParkingCode: str,
        DeviceId: str,
        LicensePlate: str,
        Type: ParkingOperationType,
    ) -> None:
        log_data = dict(
            UserId=user.Id,
            PhoneParkingCode=PhoneParkingCode,
            DeviceId=DeviceId,
            LicensePlate=LicensePlate,
            Phone=user.Phone,
            Type=Type,
            Timestamp=get_utc_millis(),
        )
        log_data = self._shade(log_data)
        self._db.put_object(ParkingOperationLog(**log_data))

    def list(self, user: User) -> List[ParkingOperationLog]:
        ret = self._db.get_objects_by_query(
            ParkingOperationLog, filters=[("UserId", "=", user.Id)], order=["Timestamp"]
        )
        return [ParkingOperationLog(**self._unshade(l)) for l in ret]
