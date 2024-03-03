import app.util.http_error as err
from app.models.carpark import SelectedCarPark
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleUpdate
from app.services.data_manager import _DataManager


class UserdataManager(_DataManager):

    def __init__(self, db, fernet):
        super().__init__(db, fernet, ["LicensePlate"])

    # carparks

    def list_carparks(self, user: User) -> list[SelectedCarPark]:
        self._db.get_objects_by_query(SelectedCarPark, [("UserId", "=", user.Id)])

    def add_carpark(
        self, user: User, CarParkId: str, PhoneParkingCode: str
    ) -> SelectedCarPark:
        exists = self._db.find_object(
            SelectedCarPark,
            filters=[("UserId", "=", user.Id), ("CarParkId", "=", CarParkId)],
        )
        if exists:
            err.conflict("Exists")
        carpark = SelectedCarPark(
            UserId=user.Id, CarParkId=CarParkId, PhoneParkingCode=PhoneParkingCode
        )
        self._db.put_object(carpark)
        return carpark

    def remove_carpark(self, user: User, id: int) -> int:
        return self._db.delete_by_query(
            SelectedCarPark, filters=[("Id", "=", id), ("UserId", "=", user.Id)]
        )

    # vehicles

    def list_vehicles(self, user: User) -> list[Vehicle]:
        vehicles = self._db.get_objects_by_query(Vehicle, [("UserId", "=", user.Id)])
        return [Vehicle(**self._unshade(v)) for v in vehicles]

    def add_vehicle(self, vehicle: Vehicle) -> Vehicle:
        shaded = Vehicle(**self._shade(vehicle))
        self._db.put_object(shaded)
        vehicle.Id = shaded.Id
        return vehicle

    def update_vehicle(self, user: User, vehicle_id: int, **data) -> Vehicle:
        vehicle = self._db.find_object(
            Vehicle, filters=[("Id", "=", vehicle_id), ("UserId", "=", user.Id)]
        )
        shaded = self._shade(data)
        updated = self._update(vehicle, shaded)
        self._db.put_object(updated)
        return Vehicle(**self._unshade(updated))

    def remove_vehicle(self, user: User, id: int) -> int:
        return self._db.delete_by_query(
            Vehicle, filters=[("Id", "=", id), ("UserId", "=", user.Id)]
        )
