from cryptography.fernet import Fernet
from pydantic import BaseModel

from .datastore import Database


class _DataManager(object):
    """Base class for data managers.

    Has database instance and encryption methods.
    """

    _db: Database
    _fernet: Fernet

    def __init__(self, db, fernet):
        self._db = db
        self._fernet = fernet

    def _shade(self, obj: BaseModel, *shaded_keys) -> BaseModel:
        """Fernet encrypt shaded_keys in the new copy of obj.

        Args:
            obj (BaseModel): Plain object

        Returns:
            BaseModel: Encrypted object
        """

        copy = obj.model_copy(deep=True)
        for k in shaded_keys:
            if hasattr(copy, k):
                setattr(
                    copy, k, self._fernet.encrypt(getattr(copy, k).encode()).decode()
                )
        return copy

    def _unshade(self, obj: BaseModel, *shaded_keys) -> BaseModel:
        """Fernet decrypt shaded_keys in the new copy of obj.

        Args:
            obj (BaseModel): Encrypted object

        Returns:
            BaseModel: Decrypted object
        """

        copy = obj.model_copy(deep=True)
        for k in shaded_keys:
            if hasattr(copy, k):
                setattr(
                    copy, k, self._fernet.decrypt(getattr(copy, k).encode()).decode()
                )
        return copy
