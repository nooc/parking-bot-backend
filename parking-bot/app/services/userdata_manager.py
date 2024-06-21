import app.util.http_error as err
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleDb
from app.services.data_manager import _DataManager


class UserdataManager(_DataManager):

    def __init__(self, db, fernet):
        super().__init__(db, fernet, ["LicensePlate"])

    # carparks

    def add_tollpark(self, user: User, carpark_id: int) -> None:
        if carpark_id in user.CarParks.Toll:
            err.conflict("Id exists.")
        user.CarParks.Toll.append(carpark_id)
        self._db.put_object(user)

    def add_kioskpark(self, user: User, carpark_id: int) -> None:
        if carpark_id in user.CarParks.Kiosk:
            err.conflict("Id exists.")
        user.CarParks.Kiosk.append(carpark_id)
        self._db.put_object(user)

    def remove_tollpark(self, user: User, carpark_id: int) -> None:
        if carpark_id in user.CarParks.Toll:
            user.CarParks.Toll.remove(carpark_id)
            self._db.put_object(user)
            return
        err.not_found("Id not found.")

    def remove_kioskpark(self, user: User, carpark_id: int) -> None:
        if carpark_id in user.CarParks.Kiosk:
            user.CarParks.Kiosk.remove(carpark_id)
            self._db.put_object(user)
            return
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
