from app.models.carpark import SelectedCarPark
from app.models.user import User, UserCreate, UserUpdate
from app.models.vehicle import Vehicle
from app.services.data_manager import _DataManager


class UserManager(_DataManager):

    __shaded_keys = ["Phone"]

    def __init__(self, db, fernet):
        super().__init__(db, fernet)

    def create_user(self, user_data: UserCreate) -> User:
        new_user = User(**user_data.model_dump())
        self._db.put_object(self._shade(new_user, *self.__shaded_keys))
        return new_user

    def get_user(self, id: str) -> User:
        return self._unshade(self._db.get_object(User, id), *self.__shaded_keys)

    def update_user(self, user: User, user_data: UserUpdate) -> User:
        update_data = user_data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(user, k, v)
        self._db.put_object(self._shade(user, *self.__shaded_keys))
        return user

    def delete_user(self, user: User) -> None:
        user_filter = [("UserId", "=", user.Id)]
        self._db.delete_by_query(SelectedCarPark, filters=user_filter)
        self._db.delete_by_query(Vehicle, filters=user_filter)
        self._db.delete_object(user)

    def list_users(self, offset=0, limit=20) -> list[User]:
        users = self._db.get_objects_by_query(User, offset=offset, limit=limit)
        return [self._unshade(u, *self.__shaded_keys) for u in users]
