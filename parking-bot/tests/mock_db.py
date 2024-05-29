import uuid
from typing import Any, Union

from cryptography.fernet import Fernet
from pydantic import BaseModel

from app.models.carpark import SelectedKioskParkDb, SelectedTollParkDb
from app.models.logs import ParkingOperationLog
from app.models.user import User, UserState
from app.models.vehicle import Vehicle
from app.util.time import get_utc_millis

type HandleType = BaseModel | tuple[type, Any]
type FilterType = tuple[str, str, Any]


# TODO fix filtering. test all filters
class Database:
    __data: dict[str, dict[Any, BaseModel]]
    __INT_ID = 1000

    _fernet: Fernet

    @classmethod
    def __pass_filter(cls, filters: list[FilterType], obj) -> bool:
        if not filters:
            return True
        for fk, fop, fval in filters:
            val = getattr(obj, fk)
            match fop:
                case "=":
                    res = val == fval
                case "<=":
                    res = val <= fval
                case ">=":
                    res = val >= fval
                case "<":
                    res = val < fval
                case ">":
                    res = val > fval
                case "!=":
                    res = val != fval
                case "IN":
                    res = val in fval
                case "NOT_IN":
                    res = val not in fval
                case _:
                    raise SyntaxError
            if not res:
                return False
        return True

    @classmethod
    def __gen_int_id(cls):
        cls.__INT_ID += 1
        return cls.__INT_ID

    @classmethod
    def __gen_str_id(cls):
        return str(uuid.uuid1())

    def __init__(self, fernet: Fernet) -> None:
        self._fernet = fernet
        data = {
            User.__name__: {},
            Vehicle.__name__: {},
            SelectedTollParkDb.__name__: {},
            SelectedKioskParkDb.__name__: {},
            ParkingOperationLog.__name__: {},
        }
        for i in range(1, 4):
            uid = f"_0a0a0a0a0a0a0a0{i}"
            data[User.__name__][uid] = User(
                Id=uid,
                State=UserState.Normal,
                Roles=["user"],
                Phone=fernet.encrypt(b"0701234567").decode(),
            )
            data[Vehicle.__name__][i] = Vehicle(
                Id=i,
                UserId=uid,
                DeviceId=f"xyz{i}",
                LicensePlate=fernet.encrypt(b"ABC10{i}").decode(),
                Name=f"Car{i}",
            )
            data[SelectedTollParkDb.__name__][i] = SelectedTollParkDb(
                Id=i,
                UserId=uid,
                CarParkId="1480 2007-03491",
                PhoneParkingCode="000",
            )
            data[SelectedKioskParkDb.__name__][i] = SelectedKioskParkDb(
                Id=i,
                UserId=uid,
                KioskId="8c1efaf6-04f5-443f-a566-0cf2e4fbd1ed",
            )
            data[ParkingOperationLog.__name__][i] = ParkingOperationLog(
                Id=i,
                UserId=uid,
                DeviceId="device1",
                LicensePlate=fernet.encrypt(b"ABC123").decode(),
                Phone=fernet.encrypt(b"0700").decode(),
                ParkingCode="123",
                Start=get_utc_millis() - 3600000,
                Stop=get_utc_millis(),
                Type="start-sms",
            )
        self.__data = data

    def get_object(self, objClass: Any, objId: Union[int, str]) -> BaseModel:
        if objClass.__name__ in self.__data:
            table = self.__data[objClass.__name__]
            if objId in table:
                return table[objId]
        raise FileNotFoundError

    def get_objects_by_id(
        self, objClass: Any, ids: list[Union[int, str]]
    ) -> list[BaseModel]:

        if objClass.__name__ in self.__data:
            res = []
            table = self.__data[objClass.__name__]
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
        if objClass.__name__ in self.__data:
            table = self.__data[objClass.__name__]
            return set(table.keys()).intersection(ids)
        return []

    def get_keys_by_query(
        self, objClass: Any, filters: list[FilterType] = None, **kwarks
    ) -> list[Union[int, str]]:
        res = []
        res = self.get_objects_by_query(objClass, filters=filters, **kwarks)
        return [o.Id for o in res]

    def get_objects_by_query(
        self, objClass: Any, filters: list[FilterType] = None, **kwarks
    ) -> list[BaseModel]:
        res = []
        if objClass.__name__ in self.__data:
            table = self.__data[objClass.__name__]
            for o in table.values():
                if filters and not self.__pass_filter(filters, o):
                    continue
                res.append(o)
            if "order" in kwarks:
                orders = kwarks["order"]
                if orders != []:
                    sort_key: str = orders[0]
                    if sort_key.startswith("-"):
                        res.sort(key=lambda e: getattr(e, sort_key[1:]), reverse=True)
                    else:
                        res.sort(key=lambda e: getattr(e, sort_key))
        return res

    def find_object(self, objClass: Any, filters: list[FilterType] = None) -> BaseModel:
        if objClass.__name__ in self.__data:
            table = self.__data[objClass.__name__]
            for o in table.values():
                if filters:
                    if not self.__pass_filter(filters, o):
                        continue
                    return o
                else:
                    return o
        return None

    def put_object(self, obj: BaseModel) -> None:
        if obj.Id == None:
            id_types = obj.model_json_schema()["properties"]["Id"]
            if "anyOf" in id_types:
                id_types = [t["type"] for t in id_types["anyOf"]]
            if "integer" in id_types:
                obj.Id = self.__gen_int_id()
            elif "string" in id_types:
                obj.Id = self.__gen_str_id()
            else:
                raise KeyError
        self.__data[type(obj).__name__][obj.Id] = obj

    def delete_object(self, handle: HandleType) -> None:
        if isinstance(handle, tuple):
            obj_type, obj_id = handle
            del self.__data[obj_type.__name__][obj_id]
        elif isinstance(handle, BaseModel):
            del self.__data[type(handle).__name__][handle.Id]
        else:
            raise KeyError

    def delete_objects(self, handles: list[HandleType]) -> None:
        for h in handles:
            self.delete_object(h)

    def delete_by_query(
        self, objClass: Any, filters: list[FilterType] = None, **kwarks
    ) -> int:
        res = 0
        if objClass.__name__ in self.__data:
            objList = list(self.__data[objClass.__name__].values())
            for obj in objList:
                if self.__pass_filter(filters=filters, obj=obj):
                    del self.__data[objClass.__name__][obj.Id]
                    res += 1
        return res

    def is_empty(self, objClass: Any, filters: list[FilterType] = None) -> bool:
        return self.get_keys_by_query(objClass, filters) == []
