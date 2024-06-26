from typing import List

from app.models.history import HistoryItem, HistoryType
from app.models.user import User


class HistoryManager:

    def __init__(self, db):
        self._db = db

    def add(
        self,
        user: User,
        type: HistoryType,
        timestamp: int,
        carpark_id: str = None,
        vehicle_id: int = None,
    ) -> HistoryItem:
        """_summary_

        Args:
            user (User): Current user
            type (HistoryType): Type of log
            timestamp (int): Timestamp as UTC seconds
            carpark_id (str, optional): CarPark id
            vehicle_id (int, optional): Vehicle id

        Returns:
            HistoryItem: _description_
        """
        log_data = dict(
            UserId=user.Id,
            Type=type,
            Timestamp=timestamp,
            CarParkId=carpark_id,
            VehicleId=vehicle_id,
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
            HistoryItem, filters=filters, order=["-Timestamp"], **args
        )
        return [HistoryItem(**self._unshade(log_item)) for log_item in ret]


__all__ = ("HistoryManager",)
