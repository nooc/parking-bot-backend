from app.models.carpark import SelectedKioskParkDb, SelectedTollParkDb
from app.models.user import User, UserState
from app.models.vehicle import VehicleDb
from app.services.data_manager import _DataManager
from app.util import http_error as err


class UserManager(_DataManager):

    _default_user_attr = {"Roles": ["user"], "State": UserState.Normal}

    def __init__(self, db, fernet):
        super().__init__(db, fernet, ["Phone"])

    def create_user(self, Id: str) -> User:
        if self._db.find_object(User, [("Id", "=", Id)]) != None:
            err.conflict("Exists.")
        plain_data = dict(Id=Id, **self._default_user_attr)
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
        user_filter = [("UserId", "=", user_id)]
        self._db.delete_by_query(SelectedTollParkDb, filters=user_filter)
        self._db.delete_by_query(SelectedKioskParkDb, filters=user_filter)
        self._db.delete_by_query(VehicleDb, filters=user_filter)
        self._db.delete_object((User, user_id))

    def list_users(self, offset=0, limit=20) -> list[User]:
        users = self._db.get_objects_by_query(User, offset=offset, limit=limit)
        return [User(**self._unshade(u)) for u in users]
