from datetime import timedelta
from time import time
from typing import Union

import app.util.http_error as err
from app.config import Settings
from app.models.carpark import CarPark
from app.models.cell import CellInfo
from app.models.external.free import FreeParkingInfo
from app.models.external.kiosk import KioskParkingInfoEx
from app.models.external.toll import TollParkingInfo
from app.services.gothenburg_open_data import CarParkDataSource
from app.services.kiosk_manager import KioskManager
from app.util.carpark_id import CarParkId
from app.util.dggs import Dggs

from .datastore import Database


class CarParkManager:

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

    def get_carpark(self, id: str) -> CarPark:
        carpark = self._db.get_object(CarPark, id)
        return carpark or err.not_found("Car park not found.")

    def get_carparks_by_cell_id(self, id: str) -> list[CarPark]:
        """Get `CarPark` objects belonging to the cell.

        Args:
            id (str): Cell id

        Returns:
            list[CarPark]: `CarPark` objects
        """
        result = self._check_cell(id)
        val = result or self._db.get_objects_by_query(CarPark, [("CellId", "=", id)])
        return val

    def _check_cell(self, id: str) -> Union[list[CarPark], None]:
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
        if info and info.Expires > time():
            return None
        return self._update_cell(id)

    def _clear_cell(self, id: str) -> None:
        self._db.delete_by_query(CarPark, [("CellId", "=", id)])

    def _update_cell(self, id: str) -> Union[list[CarPark], None]:
        """Update or create cell.

        Args:
            id (str): Cell id
        """
        parkings: list[CarPark] = []
        cell = self._dggs.get_cell(id)
        lat, lon, rad = self._dggs.cell_to_lat_lon_rad(id)

        # clear old
        self._db.delete_by_query(CarPark, [("CellId", "=", id)])

        # get toll
        tplist: list[TollParkingInfo] = self._src.get_nearby_toll_parking(
            lat=lat, lon=lon, radius=rad
        )
        # filter out edge cases not belonging to cell
        filtered = [p for p in tplist if cell.contains((p.Long, p.Lat), plane=False)]
        parkings.extend(
            [
                CarPark(
                    Id=CarParkId.toll_id(inf),
                    CellId=id,
                    Type="toll",
                    Info=inf.model_dump_json(),
                )
                for inf in filtered
            ]
        )

        # get free
        fplist: list[FreeParkingInfo] = self._src.get_nearby_free_parking(
            lat=lat, lon=lon, radius=rad
        )
        # filter out edge cases not belonging to cell
        filtered = [p for p in fplist if cell.contains((p.Long, p.Lat), plane=False)]
        parkings.extend(
            [
                CarPark(
                    Id=CarParkId.free_id(inf),
                    CellId=id,
                    Type="free",
                    Info=inf.model_dump_json(),
                )
                for inf in filtered
            ]
        )

        # get kiosks
        klist: list[KioskParkingInfoEx] = self._db.get_objects_by_query(
            KioskParkingInfoEx, [("CellId", "=", id)]
        )
        parkings.extend(
            [
                CarPark(
                    Id=CarParkId.kiosk_id(inf),
                    CellId=id,
                    Type="kiosk",
                    Info=inf.model_dump_json(),
                )
                for inf in klist
            ]
        )

        # store found
        batch = self._db.create_batch()
        for p in parkings:
            batch.put(p)
        batch.put(
            CellInfo(
                Id=id,
                Expires=int(
                    time()
                    + timedelta(days=self._cfg.DGGS_CELL_EXPIRY_DAYS).total_seconds()
                ),
            )
        )
        batch.commit()
        return parkings
