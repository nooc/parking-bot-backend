import logging
from typing import Literal

from fastapi import HTTPException, status


def __except(
    code: int, msg: str = None, level: int = logging.ERROR, do_log: bool = True
):
    if do_log:
        logging.log(level=level, do_log=do_log, msg=f"{code}: {msg}")
    raise HTTPException(status_code=code, detail=msg)


def internal(msg: str = None, level: int = logging.CRITICAL, do_log: bool = True):
    __except(status.HTTP_500_INTERNAL_SERVER_ERROR, msg=msg, level=level, do_log=do_log)


def bad_request(msg: str = None, level: int = logging.ERROR, do_log: bool = True):
    __except(status.HTTP_400_BAD_REQUEST, msg=msg, level=level, do_log=do_log)


def unauthorized(msg: str = None, level: int = logging.ERROR, do_log: bool = True):
    __except(status.HTTP_401_UNAUTHORIZED, msg=msg, level=level, do_log=do_log)


def forbidden(msg: str = None, level: int = logging.ERROR, do_log: bool = True):
    __except(status.HTTP_403_FORBIDDEN, msg=msg, level=level, do_log=do_log)


def not_found(msg: str = None, level: int = logging.WARN, do_log: bool = True):
    __except(status.HTTP_404_NOT_FOUND, msg=msg, level=level, do_log=do_log)


def conflict(msg: str = None, level: int = logging.WARN, do_log: bool = True):
    __except(status.HTTP_409_CONFLICT, msg=msg, level=level, do_log=do_log)


def locked(msg: str = None, level: int = logging.WARN, do_log: bool = True):
    __except(status.HTTP_423_LOCKED, msg=msg, level=level, do_log=do_log)


def too_early(msg: str = None, level: int = logging.WARN, do_log: bool = True):
    __except(status.HTTP_425_TOO_EARLY, msg=msg, level=level, do_log=do_log)
