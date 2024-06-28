from app.models.carpark import CarPark
from app.models.parking import ActiveParking
from app.models.user import User, UserState
from app.models.vehicle import VehicleDb
from app.util import http_error as err
from app.util.property_shader import PropertyShader

__SELECTABLE_TYPES = ["toll", "kiosk"]


class UserManager(PropertyShader):

    _SHADED = ["Phone"]
    _default_user_attr = {"Roles": ["user"], "State": UserState.Normal}

    def __init__(self, db, fernet):
        super().__init__(fernet=fernet, shaded_keys=self._SHADED)
        self._db = db

    def create_user(self, id: str) -> User:
        if self._db.find_object(User, [("Id", "=", id)]) != None:
            err.conflict("Exists.")
        plain_data = dict(Id=id, **self._default_user_attr)
        data = self._shade(plain_data)
        new_user = User(**data)
        self._db.put_object(new_user)
        return User(**plain_data)

    def get_user(self, id: str) -> User:
        """Get user from database.

        Args:
            id (str): Id

        Returns:
            User: User|None
        """
        user = self._db.get_object(User, id)
        return User(**self._unshade(user))

    def update_user(self, user: User, **update) -> User:
        # return this
        returned = user.model_copy()
        self._update(returned, **update)
        # update, shade, store
        supdate = self._shade(update)
        self._update(user, **supdate)
        self._db.put_object(user)
        return returned

    def delete_user(self, user_id: str) -> None:
        # TODO: if active toll parking, send push to end it
        user_filter = [("UserId", "=", user_id)]
        self._db.delete_by_query(ActiveParking, filters=user_filter)
        self._db.delete_by_query(VehicleDb, filters=user_filter)
        self._db.delete_object(("User", user_id))

    def list_users(self, offset=0, limit=20) -> list[User]:
        users = self._db.get_objects_by_query(User, offset=offset, limit=limit)
        return [User(**self._unshade(u)) for u in users]

    # selected carparks

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


__all__ = ("UserManager",)
