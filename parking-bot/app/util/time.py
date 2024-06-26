import time
from datetime import datetime


def get_utc_seconds() -> int:
    return int(time.time())


def get_utc_millis() -> int:
    return int(time.time() * 1000)


def get_time_string(epoc_millis: int = -1) -> str:
    if epoc_millis < 0:
        dt = datetime.now()
    else:
        dt = datetime.fromtimestamp(float(epoc_millis) / 1000)
    return dt.strftime("%e %b %Y %R UTC")
