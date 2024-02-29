from ctypes import Union
from typing import Any

from pydantic import BaseModel


class Database(object):
    # TODO: Implement

    data = {}

    def get_object(self, objClass: Any, objId: Union[int, str]) -> BaseModel:
        if objClass in self.data:
            table = self.data[objClass]
            if objId in table:
                return table[objId]
        raise FileNotFoundError

    def get_objects_by_id(
        self, objClass: Any, ids: list[Union[int, str]]
    ) -> list[BaseModel]:

        if objClass in self.data:
            res = []
            table = self.data[objClass]
            for o in table:
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
        raise NotImplementedError

    def get_objects_by_query(
        self, objClass: Any, filters: list[tuple] = None, **kwarks
    ) -> list[BaseModel]:
        raise NotImplementedError

    def find_object(self, objClass: Any, filters: list[tuple] = None) -> BaseModel:
        raise NotImplementedError

    def put_object(self, obj: BaseModel) -> None:
        raise NotImplementedError

    def delete_object(self, handle: Any) -> None:
        raise NotImplementedError

    def delete_objects(self, handles: list) -> None:
        raise NotImplementedError

    def delete_by_query(
        self, objClass: Any, filters: list[tuple] = None, **kwarks
    ) -> int:
        raise NotImplementedError

    def is_empty(self, objClass: Any, filters: list[tuple] = None) -> bool:
        raise NotImplementedError
