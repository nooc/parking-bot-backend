import logging

from fastapi import HTTPException, status


def __except(code: int, msg: str = None):
    logging.error(f"{code}: {msg}")
    raise HTTPException(status_code=code, detail=msg)


internal = lambda msg: __except(status.HTTP_500_INTERNAL_SERVER_ERROR, msg=msg)
bad_request = lambda msg: __except(status.HTTP_400_BAD_REQUEST, msg=msg)
unauthorized = lambda msg: __except(status.HTTP_401_UNAUTHORIZED, msg=msg)
forbidden = lambda msg: __except(status.HTTP_403_FORBIDDEN, msg=msg)
not_found = lambda msg: __except(status.HTTP_404_NOT_FOUND, msg=msg)
conflict = lambda msg: __except(status.HTTP_409_CONFLICT, msg=msg)
locked = lambda msg: __except(status.HTTP_423_LOCKED, msg=msg)
too_early = lambda msg: __except(status.HTTP_425_TOO_EARLY, msg=msg)
