import app.util.http_error as err
from app.models.carpark import CarPark
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleDb
from app.services.data_manager import _DataManager

__SELECTABLE_TYPES = ["toll", "kiosk"]


class UserdataManager(_DataManager):

    def __init__(self, db, fernet):
        super().__init__(db, fernet, ["LicensePlate"])

    # carparks

    def add_carpark(self, user: User, carpark_id: int) -> None:
        if carpark_id in user.CarParks:
            err.conflict("Id exists.")
        carpark: CarPark = self._db.get_object(CarPark, carpark_id) or err.not_found(
            "CarPark"
        )
        if carpark.Type in __SELECTABLE_TYPES:
            user.CarParks.append(carpark_id)
            self._db.put_object(user)
        else:
            err.bad_request("CarPark type")

    def remove_carpark(self, user: User, carpark_id: int) -> None:
        if carpark_id in user.CarParks:
            user.CarParks.remove(carpark_id)
            self._db.put_object(user)
        else:
            err.not_found("Id not found.")

    # vehicles

    def list_vehicles(self, user: User) -> list[VehicleDb]:
        vehicles = self._db.get_objects_by_query(VehicleDb, [("UserId", "=", user.Id)])
        return [VehicleDb(**self._unshade(v)) for v in vehicles]

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


__all__ = ("UserdataManager",)
