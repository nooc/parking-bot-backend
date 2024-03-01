from app.models.carpark import SelectedCarPark
from app.models.user import User, UserCreate, UserState, UserUpdate
from app.models.vehicle import Vehicle
from app.services.data_manager import _DataManager


class UserManager(_DataManager):

    _default_user_attr = {"Roles": ["user"], "State": UserState.Normal}

    def __init__(self, db, fernet):
        super().__init__(db, fernet, ["Phone"])

    def create_user(self, user_data: UserCreate) -> User:
        data = user_data.model_dump().update(**self._default_user_attr)
        sdata = self._shade(data)
        new_user = User(**sdata)
        self._db.put_object(new_user)
        return User(**data)

    def get_user(self, id: str) -> User:
        return User(**self._unshade(self._db.get_object(User, id)))

    def update_user(self, user: User, **update) -> User:
        # return this
        returned = user.model_dump()
        returned.update(**update)
        # update, shade, store
        update = self._shade(update)
        self._update(user, **update)
        self._db.put_object(user)
        return returned

    def delete_user(self, user: User) -> None:
        user_filter = [("UserId", "=", user.Id)]
        self._db.delete_by_query(SelectedCarPark, filters=user_filter)
        self._db.delete_by_query(Vehicle, filters=user_filter)
        self._db.delete_object(user)

    def list_users(self, offset=0, limit=20) -> list[User]:
        users = self._db.get_objects_by_query(User, offset=offset, limit=limit)
        return [self._unshade(u, *self.__shaded_keys) for u in users]
