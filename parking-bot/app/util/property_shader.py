import logging
from typing import Any

from cryptography.fernet import Fernet
from pydantic import BaseModel


class PropertyShader(object):
    """Base class for data managers.

    Has database instance and encryption methods.
    """

    _fernet: Fernet
    _shaded_keys: list[str]

    def __init__(self, fernet, shaded_keys):
        self._fernet = fernet
        self._shaded_keys = shaded_keys

    def _shade(self, obj: BaseModel | dict) -> dict[str, Any]:
        """Fernet encrypt shaded keys in the new copy of obj.

        Args:
            obj (BaseModel|dict): object to shade

        Returns:
            dict: Encrypted dict
        """
        if isinstance(obj, BaseModel):
            copy = obj.model_dump(exclude_unset=True)
        else:
            copy = obj.copy()
        for k, v in copy.items():
            if k in self._shaded_keys:
                copy[k] = self._fernet.encrypt(v.encode()).decode()
        return copy

    def _unshade(self, obj: BaseModel | dict) -> dict[str, Any]:
        """Fernet decrypt shaded keys in the new copy of obj.

        Args:
            obj (BaseModel): Encrypted object

        Returns:
            BaseModel: Decrypted object
        """

        if isinstance(obj, BaseModel):
            copy = obj.model_dump(exclude_unset=True)
        else:
            copy = obj.copy()
        for k, v in copy.items():
            if k in self._shaded_keys:
                try:
                    copy[k] = self._fernet.decrypt(v).decode()
                except Exception as ex:
                    logging.warning(str(ex))
                    copy[k] = None
        return copy

    def _update(cls, target: BaseModel, **source) -> BaseModel:
        """Update attributes from source if they exist.

        Args:
            target (BaseModel): Update target
            source (dict): Update source

        Returns:
            BaseModel: Ref to target
        """
        for k, v in source.items():
            if hasattr(target, k):
                setattr(target, k, v)
        return target


__all__ = ("PropertyShader",)
