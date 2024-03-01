from typing import List
from app.models.logs import ParkingOperationLog
from app.models.user import User
from app.services.data_manager import _DataManager


class ParkingLogManager(_DataManager):

    def __init__(self, db, fernet):
        super().__init__(db, fernet, ["LicensePlate", "Phone"])

    def log(self, operation: ParkingOperationLog) -> None:
        return self._db.put_object(operation)

    def list(self, user:User) -> List[ParkingOperationLog]:
        
