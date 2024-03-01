import uuid
from typing import Any, Union

from pydantic import BaseModel

from app.models.carpark import SelectedCarPark
from app.models.user import User, UserState
from app.models.vehicle import Vehicle


class Database:
    __data: dict[type, dict[Any, BaseModel]]
    __INT_ID = 1000

    @classmethod
    def __pass_filter(cls, filters: tuple[str, str, Any], obj) -> bool:
        for f in filters:
            if hasattr(obj, f[0]):
                v = getattr(obj, f[0])
                match f[1]:
                    case "=":
                        return v == f[2]
                    case "<=":
                        return v <= f[2]
                    case ">=":
                        return v >= f[2]
                    case "<":
                        return v < f[2]
                    case ">":
                        return v > f[2]
                    case "!=":
                        return v != f[2]
                    case "IN":
                        return v in f[2]
                    case "NOT_IN":
                        return v not in f[2]
                    case _:
                        raise SyntaxError
            else:
                return False
        return True

    @classmethod
    def __gen_int_id(cls):
        cls.__INT_ID += 1
        return cls.__INT_ID

    @classmethod
    def __gen_str_id(cls):
        return str(uuid.uuid1())

    def __init__(self) -> None:
        users = {}
        vehicles = {}
        carparks = {}
        for i in range(1, 4):
            users[f"user-{i}"] = User(
                Id=f"user-{i}",
                State=UserState.Normal,
                Roles=["user"],
                Phone="0701234567",
            )
            vehicles[i] = Vehicle(
                Id=i,
                UserId=f"user-{i}",
                DeviceId=f"xyz{i}",
                LicensePlate="ABC10{i}",
                Name=f"Car{i}",
            )
            carparks[i] = SelectedCarPark(
                Id=i, UserId=f"user-{i}", CarParkId="1480 2007-03491"
            )
        self.__data = {User: users, Vehicle: vehicles, SelectedCarPark: carparks}

    def get_object(self, objClass: Any, objId: Union[int, str]) -> BaseModel:
        if objClass in self.__data:
            table = self.__data[objClass]
            if objId in table:
                return table[objId]
        raise FileNotFoundError

    def get_objects_by_id(
        self, objClass: Any, ids: list[Union[int, str]]
    ) -> list[BaseModel]:

        if objClass in self.__data:
            res = []
            table = self.__data[objClass]
            for o in table.values():
                if o.Id in ids:
                    res.append(o)
                else:
                    raise FileNotFoundError
            return res
        raise FileNotFoundError

    def verify_object_ids(
        self, objClass: Any, ids: list[Union[int, str]]
    ) -> list[Union[int, str]]:
        raise NotImplementedError

    def get_keys_by_query(
        self, objClass: Any, filters: list[tuple] = None, **kwarks
    ) -> list[Union[int, str]]:
        res = []
        if objClass in self.__data:
            table = self.__data[objClass]
            for o in table.values():
                if filters and not self.__pass_filter(filters, o):
                    continue
                res.append(o.Id)
        return res

    def get_objects_by_query(
        self, objClass: Any, filters: list[tuple] = None, **kwarks
    ) -> list[BaseModel]:
        res = []
        if objClass in self.__data:
            table = self.__data[objClass]
            for o in table.values():
                if filters and not self.__pass_filter(filters, o):
                    continue
                res.append(o)
        return res

    def find_object(self, objClass: Any, filters: list[tuple] = None) -> BaseModel:
        if objClass in self.__data:
            table = self.__data[objClass]
            for o in table.values():
                if filters:
                    if not self.__pass_filter(filters, o):
                        continue
                    return o
                else:
                    return o
        return None

    def put_object(self, obj: BaseModel) -> None:
        t = obj.model_json_schema()["properties"]["Id"]["type"]
        if obj.Id == None:
            if t == "integer":
                obj.Id = self.__gen_int_id()
            else:
                obj.Id = self.__gen_str_id()
        self.__data[type(obj)][obj.Id] = obj

    def delete_object(self, handle: Any) -> None:
        if handle is tuple:
            del self.__data[handle[0]][handle[1]]
        elif isinstance(handle, BaseModel):
            del self.__data[type(handle)][handle.Id]

    def delete_objects(self, handles: list) -> None:
        for h in handles:
            self.delete_object(h)

    def delete_by_query(
        self, objClass: Any, filters: list[tuple] = None, **kwarks
    ) -> int:
        res = 0
        keys = self.get_keys_by_query(objClass, filters)
        for k in keys:
            del self.__data[objClass][k]
            res += 1
        return res

    def is_empty(self, objClass: Any, filters: list[tuple] = None) -> bool:
        return self.get_keys_by_query(objClass, filters) == []
