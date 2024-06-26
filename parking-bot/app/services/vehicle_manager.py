import app.util.http_error as err
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleDb
from app.services.data_manager import _DataManager


class VehicleManager(_DataManager):
    _SHADED = ["Phone", "LicensePlate"]

    def __init__(self, db, fernet):
        super().__init__(db, fernet, self._SHADED)

    # vehicles

    def list_vehicles(self, user: User) -> list[VehicleDb]:
        vehicles = self._db.get_objects_by_query(VehicleDb, [("UserId", "=", user.Id)])
        return [VehicleDb(**self._unshade(v)) for v in vehicles]

    def get_vehicle(self, id: int) -> VehicleDb:
        vehicle = self._db.get_object(VehicleDb, id)
        if not vehicle:
            err.not_found()
        return VehicleDb(**self._unshade(vehicle))

    def add_vehicle(self, user: User, vehicle: Vehicle) -> VehicleDb:
        shaded = VehicleDb(UserId=user.Id, **self._shade(vehicle))
        self._db.put_object(shaded)
        return VehicleDb(**self._unshade(shaded))

    def update_vehicle(self, user: User, vehicle_id: int, **data) -> VehicleDb:
        vehicle = self._db.find_object(
            VehicleDb, filters=[("Id", "=", vehicle_id), ("UserId", "=", user.Id)]
        )
        shaded = self._shade(data)
        updated = self._update(vehicle, shaded)
        self._db.put_object(updated)
        return VehicleDb(**self._unshade(updated))

    def remove_vehicle(self, id: int) -> int:
        self._db.delete_object(("VehicleDb", id))
        return 1


__all__ = ("VehicleManager",)
