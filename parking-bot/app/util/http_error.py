import logging

from fastapi import HTTPException, status


def __except(message: str = None):
    raise HTTPException(status.HTTP_400_BAD_REQUEST, message)


def internal(m):
    logging.error(m)
    __except(None, status.HTTP_500_INTERNAL_SERVER_ERROR)


bad_request = lambda m: __except(m, status.HTTP_400_BAD_REQUEST)
unauthorized = lambda m: __except(m, status.HTTP_401_UNAUTHORIZED)
forbidden = lambda m: __except(m, status.HTTP_403_FORBIDDEN)
not_found = lambda m: __except(m, status.HTTP_404_NOT_FOUND)
conflict = lambda m: __except(m, status.HTTP_409_CONFLICT)
locked = lambda m: __except(m, status.HTTP_423_LOCKED)
too_early = lambda m: __except(m, status.HTTP_425_TOO_EARLY)
