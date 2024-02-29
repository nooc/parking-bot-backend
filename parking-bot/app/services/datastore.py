import logging
from typing import Any, Union

from google.cloud.datastore import Batch, Client, Entity, Key
from pydantic import BaseModel

import app.util.http_error as err


def to_key(client: Client, handle: Any) -> Key:
    if isinstance(handle, Key):
        # google.cloud.datastore.Key
        return handle
    elif isinstance(handle, BaseModel):
        # schemas.*
        return client.key(type(handle).__name__, handle.Id)
    elif (
        isinstance(handle, tuple)
        and len(handle) == 2
        and type(handle[0]) == str
        and type(handle[1]) in (str, int)
    ):
        # Tuple[str, Union[int,str]]
        return client.key(handle[0], handle[1])
    return None


def to_entity(client: Client, obj: BaseModel) -> Entity:
    properties = obj.model_dump(exclude_unset=True)
    obj_id = properties.pop("Id", None)
    cls = obj.__class__.__name__
    if obj_id:
        k = client.key(cls, obj_id)
    else:
        k = client.key(cls)
    entity = Entity(k)
    entity.update(**properties)
    return entity


class BatchOperation(object):
    batch: Batch = None
    client: Client = None

    def __init__(self, client: Client):
        self.client = client
        self.batch = client.batch()
        self.batch.begin()

    def delete(self, handle: Any):
        k = to_key(self.client, handle)
        self.batch.delete(k)

    def put(self, obj: BaseModel):
        entity = to_entity(self.client, obj)
        self.batch.put(entity)

    def commit(self) -> bool:
        try:
            self.batch.commit()
        except:
            return False
        return True


class Database(object):
    """
    Serves as app database.
    """

    client: Client

    def __init__(self, cred: Union[dict, str]):
        """Construct Database.

        Args:
            cred (_type_): dict or json file path
        """

        if isinstance(cred, dict):
            self.client = Client.from_service_account_info(cred)
        elif isinstance(cred, str):
            self.client = Client.from_service_account_json(cred)
        else:
            raise TypeError("cred must be dict or str.")

    def get_object(self, objClass: Any, objId: Union[int, str]) -> BaseModel:
        """Get object from database

        Args:
            objClass (Any): Class of item.
            objId (int): Item id.

        Returns:
            BaseModel: Instance of object.

        Raises: HTTPException
        """
        try:
            key = self.client.key(objClass.__name__, objId)
            ent = self.client.get(key)
            if ent:
                properties = dict(ent.items())
                return objClass(Id=objId, **properties)
        except ValueError as ex:
            logging.error(str(ex))
            err.bad_request(str(ex))

    def get_objects_by_id(
        self, objClass: Any, ids: list[Union[int, str]]
    ) -> list[BaseModel]:
        """Get objects by their ids.

        Args:
            objClass (Any): _description_
            ids (list[Union[int,str]]): _description_

        Returns:
            list[BaseModel]: _description_

        Raises: HTTPException
        """
        try:
            res = self.client.get_multi(
                [self.client.key(objClass.__name__, id) for id in ids]
            )
            ret = []
            for e in res:
                properties = dict(e.items())
                ret.append(objClass(Id=e.key.id, **properties))
            return ret
        except Exception as ex:
            logging.error(str(ex))
            err.bad_request(str(ex))

    def verify_object_ids(
        self, objClass: Any, ids: list[Union[int, str]]
    ) -> list[Union[int, str]]:
        """_summary_

        Args:
            objClass (Any): _description_
            ids (list[Union[int,str]]): _description_

        Returns:
            list[Union[int,str]]: _description_

        Raises: HTTPException
        """
        try:
            res = self.client.get_multi(
                [self.client.key(objClass.__name__, id) for id in ids],
            )
            return [e.key.id for e in res]
        except Exception as ex:
            logging.error(str(ex))
            err.bad_request(str(ex))

    def get_keys_by_query(
        self, objClass: Any, filters: list[tuple] = None, **kwarks
    ) -> list[Union[int, str]]:
        """Get list of keys by query.

        Args:
            objClass (Any): Type
            filters (list[tuple], optional): Query filters. Defaults to None.

        Returns:
            list[Any]: List of keys in string or int form depending on entitys key format.

        Raises: HTTPException
        """
        query = self.client.query(kind=objClass.__name__)
        query.keys_only()
        if filters:
            for filter in filters:
                query = query.add_filter(*filter)
        try:
            keyList = list(query.fetch(**kwarks))
            return [k.id for k in keyList]
        except Exception as ex:
            logging.error(str(ex))
            err.bad_request(str(ex))

    def get_objects_by_query(
        self, objClass: Any, filters: list[tuple] = None, **kwarks
    ) -> list[BaseModel]:
        """[summary]

        Args:
            objClass (Any): Class of items.
            filters (list): List of filters (see. google.cloud.datastore.Query)
            **kwarks: Passed to fetch.
        Returns:
            list[BaseModel]: [description]

        Raises: HTTPException
        """
        query = self.client.query(kind=objClass.__name__)
        try:
            if filters:
                for filter in filters:
                    query = query.add_filter(*filter)
            entList = list(query.fetch(**kwarks))
            resultSet = []
            for ent in entList:
                properties = dict(ent.items())
                obj = objClass(Id=ent.key.id, **properties)
                resultSet.append(obj)
            return resultSet
        except Exception as ex:
            logging.error(str(ex))
            err.bad_request("get_objects_by_query")

    def find_object(self, objClass: Any, filters: list[tuple] = None) -> BaseModel:
        """_summary_

        Args:
            objClass (Any): _description_
            filters (list[tuple], optional): _description_. Defaults to None.

        Returns:
            BaseModel: _description_

        Raises: HTTPException
        """
        res = self.get_objects_by_query(objClass, filters=filters)
        if res:
            return res[0]
        return None

    def put_object(self, obj: BaseModel) -> None:
        """[summary]

        Args:
            obj (BaseModel): [description]

        Raises: HTTPException
        """
        entity = to_entity(self.client, obj)
        try:
            self.client.put(entity)
            if obj.Id == None:
                if entity.key.id:
                    obj.Id = entity.key.id
                else:
                    err.internal("database error")
        except Exception as ex:
            logging.error(str(ex))
            err.internal("put_object")

    def delete_object(self, handle: Any) -> None:
        """Delete an object by handle (Key or instance or tuple(class, id))

        Args:
            handle (Any): [description]

        Raises: HTTPException
        """
        try:
            self.client.delete(to_key(handle))
        except Exception as ex:
            logging.error(ex)
            err.internal("delete_object")

    def delete_objects(self, handles: list) -> None:
        """delete objects

        Args:
            handles (list): [HANDLE, ...]

            HANDLE = <Key> | (<class name>,<id[int|str]>) | <instance>

        Raises: HTTPException
        """
        try:
            self.client.delete_multi([to_key(h) for h in handles if h])
        except Exception as ex:
            logging.error(ex)
            err.internal("delete_objects")

    def delete_by_query(
        self, objClass: Any, filters: list[tuple] = None, **kwarks
    ) -> int:
        """delete by query

        Args:
            objClass (Any): _description_
            filters (list[tuple], optional): _description_. Defaults to None.

        Returns:
            int: count

        Raises: HTTPException
        """
        try:
            query = self.client.query(kind=objClass.__name__, **kwarks)
            if filters:
                for filter in filters:
                    query = query.add_filter(*filter)
            query.keys_only()
            result = list(query.fetch())
            self.client.delete_multi(result)
            return len(result)
        except Exception as ex:
            logging.error(ex)
            err.internal("delete_by_query")

    def is_empty(self, objClass: Any, filters: list[tuple] = None) -> bool:
        try:
            query = self.client.query(kind=objClass.__name__)
            if filters:
                for filter in filters:
                    query = query.add_filter(*filter)
            query.keys_only()
            return list(query.fetch(limit=1)) == []
        except Exception as ex:
            logging.error(ex)
            err.internal("is_empty")

    def create_batch(self) -> BatchOperation:
        return BatchOperation(self.client)


__all__ = (Database, BatchOperation)
