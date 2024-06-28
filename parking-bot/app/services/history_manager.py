from typing import List

from app.models.history import HistoryItem, HistoryType
from app.models.user import User
from app.services.datastore import Database


class HistoryManager:

    def __init__(self, db: Database):
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
        item = HistoryItem(
            UserId=user.Id,
            Type=type,
            Timestamp=timestamp,
            CarParkId=carpark_id,
            VehicleId=vehicle_id,
        )
        self._db.put_object(item)
        return item

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
        return ret


__all__ = ("HistoryManager",)
