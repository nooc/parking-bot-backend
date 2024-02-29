import app.util.http_error as err
from app.models.carpark import SelectedCarPark
from app.models.user import User
from app.models.vehicle import Vehicle
from app.services.data_manager import _DataManager


class UserdataManager(_DataManager):

    __shaded_keys = ["LicensePlate"]

    def __init__(self, db, fernet):
        super().__init__(db, fernet)

    # carparks

    def list_carparks(self, user: User) -> list[SelectedCarPark]:
        self._db.get_objects_by_query(SelectedCarPark, [("UserId", "=", user.Id)])

    def add_carpark(self, user: User, carpark: SelectedCarPark) -> SelectedCarPark:
        if carpark.UserId:
            if not "admin" in user.Roles:
                err.unauthorized()
        else:
            carpark.UserId = user.Id
        return carpark

    def remove_carpark(self, user: User, id: int) -> None:
        filters = [("Id", "=", id)]
        if not "admin" in user.Roles:
            filters.append(("UserId", "=", user.Id))
        self._db.delete_by_query(SelectedCarPark, filters=filters)

    # vehicles

    def list_vehicles(self, user: User) -> list[Vehicle]:
        vehicles = self._db.get_objects_by_query(Vehicle, [("UserId", "=", user.Id)])
        return [self._unshade(v, *self.__shaded_keys) for v in vehicles]

    def add_vehicle(self, user: User, vehicle: Vehicle) -> Vehicle:
        shaded: Vehicle = self._shade(vehicle, *self.__shaded_keys)
        if vehicle.UserId != user.Id:
            if not "admin" in user.Roles:
                err.unauthorized()
        else:
            shaded.UserId = user.Id
        self._db.put_object(shaded)
        vehicle.Id = shaded.Id
        return vehicle

    def remove_vehicle(self, user: User, id: int) -> None:
        filters = [("Id", "=", id)]
        if not "admin" in user.Roles:
            filters.append(("UserId", "=", user.Id))
        self._db.delete_by_query(Vehicle, filters=filters)
