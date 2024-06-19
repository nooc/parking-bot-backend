from datetime import timedelta
from hashlib import blake2s
from time import time

from app.config import Settings
from app.models.carpark import CarPark, Kiosk
from app.models.cell import CellInfo
from app.models.external.free import FreeParkingInfo
from app.models.external.kiosk import KioskParkingInfo
from app.models.external.toll import TollParkingInfo
from app.services.gothenburg_open_data import CarParkDataSource
from app.services.kiosk_manager import KioskManager
from app.util.dggs import Dggs

from .datastore import Database


class CarParkDataManager:

    def __init__(
        self,
        db: Database,
        source: CarParkDataSource,
        dggs: Dggs,
        cfg: Settings,
        kiosk: KioskManager,
    ) -> None:
        self._db = db
        self._src = source
        self._dggs = dggs
        self._cfg = cfg
        self._kiosk = kiosk

    def get_carparks_by_cell_id(self, id: str) -> list[CarPark]:
        """Get `CarPark` objects belonging to the cell.

        Args:
            id (str): Cell id

        Returns:
            list[CarPark]: `CarPark` objects
        """
        self._check_cell(id)
        result = self._db.get_objects_by_query(CarPark, [("CellId", "=", id)])
        return result

    def _check_cell(self, id: str) -> None:
        """Check cell by doing the following:

        If Exists
            If Expired
                Delete `CarPark` items belonging to cell.

                Query for parkings at cell position and re-add `CarPark` items.
            Else
                Return `CarPark` items belonging to cell.
        Else
            Query for parkings at cell position and add `CarPark` items.

        Args:
            id (str): _description_
        """
        info: CellInfo = self._db.get_object(CellInfo, id)
        if info:
            if info.Expires < time():
                self._update_cell(id)
        else:
            self._update_cell(id)

    def _clear_cell(self, id: str) -> None:
        self._db.delete_by_query(CarPark, [("CellId", "=", id)])

    def _update_cell(self, id: str) -> None:
        """Update or create cell.

        Args:
            id (str): Cell id
        """
        parkings: list[CarPark] = []
        lat, lon, area = self._dggs.cell_to_lat_lon_area(id)

        old_set = self._db.get_keys_by_query(CarPark, [("CellId", "=", id)])

        # TODO: figure out radius from area
        rad = 500

        # get toll
        tplist: list[TollParkingInfo] = self._src.get_nearby_toll_parking(
            lat=lat, lon=lon, radius=rad
        )
        parkings.extend(
            [
                CarPark(
                    Id=self._toll_id(inf),
                    CellId=id,
                    Type="toll",
                    Info=inf.model_dump_json(),
                )
                for inf in tplist
            ]
        )

        # get free
        fplist: list[FreeParkingInfo] = self._src.get_nearby_free_parking(
            lat=lat, lon=lon, radius=rad
        )
        parkings.extend(
            [
                CarPark(
                    Id=self._free_id(inf),
                    CellId=id,
                    Type="free",
                    Info=inf.model_dump_json(),
                )
                for inf in fplist
            ]
        )

        # get kiosks
        kiosks: list[Kiosk] = self._db.get_objects_by_query(
            Kiosk, [("CellId", "=", id)]
        )
        kplist = self._kiosk.get_checked([k.Id for k in kiosks])
        parkings.extend(
            [
                CarPark(
                    Id=self._kiosk_id(inf),
                    CellId=id,
                    Type="kiosk",
                    Info=inf.model_dump_json(),
                )
                for inf in kplist
            ]
        )

        # store found
        batch = self._db.create_batch()
        for p in parkings:
            batch.put(p)
        batch.put(
            CellInfo(
                Id=id,
                Expires=time()
                + timedelta(days=self._cfg.DGGS_CELL_EXPIRY_DAYS).total_seconds(),
            )
        )
        batch.commit()

    @classmethod
    def _toll_id(cl, inf: TollParkingInfo) -> str:
        hasher = blake2s(data=f"{inf.Id}{inf.Lat}{inf.Long}", digest_size=10)
        return "to" + hasher.hexdigest()

    @classmethod
    def _free_id(cl, inf: FreeParkingInfo) -> str:
        hasher = blake2s(data=f"{inf.Id}{inf.Lat}{inf.Long}", digest_size=10)
        return "fr" + hasher.hexdigest()

    @classmethod
    def _kiosk_id(cl, inf: KioskParkingInfo) -> str:
        return "ki" + inf.externalId
