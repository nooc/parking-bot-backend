import logging

from fastapi import HTTPException, status


def __except(code: int, msg: str = None):
    logging.error(f"{code}: {msg}")
    raise HTTPException(status_code=code, detail=msg)


def internal(msg: str = None):
    __except(status.HTTP_500_INTERNAL_SERVER_ERROR, msg=msg)


def bad_request(msg: str = None):
    __except(status.HTTP_400_BAD_REQUEST, msg=msg)


def unauthorized(msg: str = None):
    __except(status.HTTP_401_UNAUTHORIZED, msg=msg)


def forbidden(msg: str = None):
    __except(status.HTTP_403_FORBIDDEN, msg=msg)


def not_found(msg: str = None):
    __except(status.HTTP_404_NOT_FOUND, msg=msg)


def conflict(msg: str = None):
    __except(status.HTTP_409_CONFLICT, msg=msg)


def locked(msg: str = None):
    __except(status.HTTP_423_LOCKED, msg=msg)


def too_early(msg: str = None):
    __except(status.HTTP_425_TOO_EARLY, msg=msg)
