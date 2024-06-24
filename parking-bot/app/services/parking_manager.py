import app.util.http_error as err
from app.config import Settings
from app.models.user import User
from app.services.datastore import Database
from app.services.task_manager import TaskManager


# TODO: parking manager
class ParkingManager:

    def __init__(self, db: Database, cfg: Settings, tasks: TaskManager) -> None:
        self._db = db
        self._cfg = cfg
        self._tasks = tasks

    def request(self, user: User, carpark_id: str) -> None:
        err.internal(f"Not implemented: {__name__}")

    def delete(self, user: User, parking_id: str) -> None:
        # messaging.Message()
        err.internal(f"Not implemented: {__name__}")
