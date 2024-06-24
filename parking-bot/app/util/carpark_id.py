from hashlib import blake2s
from struct import pack

from app.models.external.free import FreeParkingInfo
from app.models.external.kiosk import KioskParkingInfo
from app.models.external.toll import TollParkingInfo


class CarParkId:

    @classmethod
    def toll_id(cl, inf: TollParkingInfo) -> str:
        hasher = blake2s(digest_size=10)
        hasher.update(inf.Id.encode())
        hasher.update(pack("f", inf.Lat))
        hasher.update(pack("f", inf.Long))
        return hasher.hexdigest()

    @classmethod
    def free_id(cl, inf: FreeParkingInfo) -> str:
        hasher = blake2s(digest_size=10)
        hasher.update(inf.Id.encode())
        hasher.update(pack("f", inf.Lat))
        hasher.update(pack("f", inf.Long))
        return hasher.hexdigest()

    @classmethod
    def kiosk_id(cl, inf: KioskParkingInfo) -> str:
        hasher = blake2s(digest_size=10)
        hasher.update(inf.externalId)
        return hasher.hexdigest()
