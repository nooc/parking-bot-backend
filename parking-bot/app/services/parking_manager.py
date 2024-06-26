import app.util.http_error as err
from app.config import Settings
from app.models.carpark import CarPark
from app.models.external.kiosk import KioskParkingInfoEx
from app.models.parking import ActiveParking
from app.models.user import User
from app.models.vehicle import VehicleDb
from app.services.carpark_manager import CarParkManager
from app.services.datastore import Database
from app.services.history_manager import HistoryManager
from app.services.kiosk_manager import AssignmentResponse, KioskManager
from app.services.task_manager import TaskManager
from app.services.vehicle_manager import VehicleManager
from app.util.time import get_utc_seconds


class ParkingManager:

    def __init__(
        self,
        db: Database,
        cfg: Settings,
        tasks: TaskManager,
        carparks: CarParkManager,
        vehicles: VehicleManager,
        history: HistoryManager,
        kiosk: KioskManager,
    ) -> None:
        self._db = db
        self._cfg = cfg
        self._tasks = tasks
        self._carparks = carparks
        self._vehicles = vehicles
        self._history = history
        self._kiosk = kiosk

    def request(self, user: User, carpark_id: str, vehicle_id: int) -> None:
        active: list[ActiveParking] = self._db.get_objects_by_query(
            ActiveParking, [("VehicleId", "=", vehicle_id)]
        )
        if not user.PushToken:
            err.bad_request("No push token.")
        if active:
            err.conflict("Vehicle already parked.")
        vehicle = self._vehicles.get_vehicle(vehicle_id)
        carpark = self._carparks.get_carpark(carpark_id)
        match carpark.Type:
            case "kiosk":
                self.__request_kiosk(user, vehicle, carpark)
            case "toll":
                self.__request_toll(user, vehicle, carpark)
            case _:
                err.internal("Unknown car park type.")
        self._history.add(
            user=user,
            type="create-parking",
            timestamp=get_utc_seconds(),
            carpark_id=carpark_id,
            vehicle_id=vehicle_id,
        )

    def delete(self, user: User, parking_id: int) -> None:
        if not user.PushToken:
            err.bad_request("No push token.")
        active: ActiveParking = self._db.get_object(ActiveParking, parking_id)
        if not active:
            err.not_found()
        self._db.delete_object(active)
        self._history.add(
            user=user,
            type="delete-parking",
            timestamp=get_utc_seconds(),
            carpark_id=active.CarParkId,
            vehicle_id=active.VehicleId,
        )

    def __request_kiosk(self, user: User, vehicle: VehicleDb, carpark: CarPark) -> None:
        kiosk = KioskParkingInfoEx.model_validate_json(carpark.Info)
        status, response = self._kiosk.try_park(user=user, kiosk=kiosk, vehicle=vehicle)
        match status:
            case AssignmentResponse.OK:
                self.__push_kiosk_success()
            case AssignmentResponse.FULL:
                self.__push_kiosk_full()
            case AssignmentResponse.UNAVAILABLE:
                self.__push_kiosk_unavailable()
            case _:
                raise RuntimeError()

    def __request_toll(self, user, vehicle, carpark) -> None:
        # TODO: create active parking and send id
        raise NotImplementedError(__name__)

    def __push_kiosk_success():
        pass  # TODO: __push_kiosk_success

    def __push_kiosk_full():
        pass  # TODO: __push_kiosk_full

    def __push_kiosk_unavailable():
        pass  # TODO: __push_kiosk_unavailable
