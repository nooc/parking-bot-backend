import app.util.http_error as err
from app.models.carpark import SelectedKioskParkDb, SelectedTollParkDb
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleDb
from app.services.data_manager import _DataManager


class UserdataManager(_DataManager):

    def __init__(self, db, fernet):
        super().__init__(db, fernet, ["LicensePlate"])

    # carparks

    def list_toll_carparks(self, user: User) -> list[SelectedTollParkDb]:
        self._db.get_objects_by_query(SelectedTollParkDb, [("UserId", "=", user.Id)])

    def list_kiosk_carparks(self, user: User) -> list[SelectedKioskParkDb]:
        self._db.get_objects_by_query(SelectedKioskParkDb, [("UserId", "=", user.Id)])

    def add_tollpark(
        self, user: User, CarParkId: str, PhoneParkingCode: str
    ) -> SelectedTollParkDb:
        exists = self._db.find_object(
            SelectedTollParkDb,
            filters=[("UserId", "=", user.Id), ("CarParkId", "=", CarParkId)],
        )
        if exists:
            err.conflict("Exists")
        carpark = SelectedTollParkDb(
            UserId=user.Id, CarParkId=CarParkId, PhoneParkingCode=PhoneParkingCode
        )
        self._db.put_object(carpark)
        return carpark

    def add_kiosk(self, user: User, KioskId: str) -> SelectedKioskParkDb:
        exists = self._db.find_object(
            SelectedKioskParkDb,
            filters=[("UserId", "=", user.Id), ("KioskId", "=", KioskId)],
        )
        if exists:
            err.conflict("Exists")
        kiosk = SelectedKioskParkDb(UserId=user.Id, KioskId=KioskId)
        self._db.put_object(kiosk)
        return kiosk

    def remove_tollpark(self, user: User, id: int) -> int:
        return self._db.delete_by_query(
            SelectedTollParkDb, filters=[("Id", "=", id), ("UserId", "=", user.Id)]
        )

    def remove_kiosk(self, user: User, id: int) -> int:
        return self._db.delete_by_query(
            SelectedKioskParkDb, filters=[("Id", "=", id), ("UserId", "=", user.Id)]
        )

    # vehicles

    def list_vehicles(self, user: User) -> list[VehicleDb]:
        vehicles = self._db.get_objects_by_query(VehicleDb, [("UserId", "=", user.Id)])
        return [VehicleDb(**self._unshade(v)) for v in vehicles]

    def add_vehicle(self, user: User, vehicle: Vehicle) -> VehicleDb:
        shaded = VehicleDb(UserId=user.Id, **self._shade(vehicle))
        self._db.put_object(shaded)
        vehicle.Id = shaded.Id
        return vehicle

    def update_vehicle(self, user: User, vehicle_id: int, **data) -> VehicleDb:
        vehicle = self._db.find_object(
            VehicleDb, filters=[("Id", "=", vehicle_id), ("UserId", "=", user.Id)]
        )
        shaded = self._shade(data)
        updated = self._update(vehicle, shaded)
        self._db.put_object(updated)
        return VehicleDb(**self._unshade(updated))

    def remove_vehicle(self, user: User, id: int) -> int:
        return self._db.delete_by_query(
            VehicleDb, filters=[("Id", "=", id), ("UserId", "=", user.Id)]
        )
