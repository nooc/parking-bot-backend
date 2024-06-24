from typing import List

from haversine import Unit, haversine
from rhealpixdggs.dggs import WGS84_ELLIPSOID, Cell, RHEALPixDGGS

DEFAULT_RESOLUTION = 9
RAD_MARGIN = 10  # m


class Dggs:
    """Dggs helper using RHEALPixDGGS.

    see: https://raichev.net/files/rhealpix_dggs_preprint.pdf


    resolution  area_m2  sqrt_area_m  cell_count
    --------------------------------------------
    0           8.5E+13  9.2E+06      6
    1           9.5E+12  3.1E+06      54
    2           1.1E+12  1E+06        4.9E+02
    3           1.2E+11  3.4E+05      4.4E+03
    4           1.3E+10  1.1E+05      3.9E+04
    5           1.4E+09  3.8E+04      3.5E+05
    6           1.6E+08  1.3E+04      3.2E+06
    7           1.8E+07  4.2E+03      2.9E+07
    8           2E+06    1.4E+03      2.6E+08
    9           2.2E+05  4.7E+02      2.3E+09
    10          2.4E+04  1.6E+02      2.1E+10
    11          2.7E+03  52           1.9E+11
    12          3E+02    17           1.7E+12
    13          33       5.8          1.5E+13
    14          3.7      1.9          1.4E+14
    15          0.41     0.64         1.2E+15
    """

    RDGGS = RHEALPixDGGS(ellipsoid=WGS84_ELLIPSOID)
    VERTEX_OFFT = 0.001
    resolution = DEFAULT_RESOLUTION

    def __init__(self, resolution: int = 9):
        self.resolution = resolution

    def __str2id(self, suid: str) -> tuple:
        return [suid[0]] + [int(e) for e in suid[1:]]

    def __reduce(self, c: Cell, res: int) -> Cell:
        if c.resolution > res:
            cell = self.RDGGS.cell(c.suid[:-1])
            return self.__reduce(cell, res)
        return c

    def __get_quad_neighbors(self, c: Cell, res: int) -> List[Cell]:
        """_summary_

        Args:
            c (Cell): _description_
            res (int): _description_

        Returns:
            List[Cell]: _description_
        """
        c = self.__reduce(c, res)
        cl: list[Cell] = []
        vert = c.vertices(plane=False)
        nwx, nwy = vert[0]
        nex, ney = vert[1]
        sex, sey = vert[2]
        swx, swy = vert[3]
        cl.append(
            self.RDGGS.cell_from_point(
                res, (nwx - self.VERTEX_OFFT, nwy + self.VERTEX_OFFT), plane=False
            )
        )
        cl.append(
            self.RDGGS.cell_from_point(
                res, (nex + self.VERTEX_OFFT, ney + self.VERTEX_OFFT), plane=False
            )
        )
        cl.append(
            self.RDGGS.cell_from_point(
                res, (sex + self.VERTEX_OFFT, sey - self.VERTEX_OFFT), plane=False
            )
        )
        cl.append(
            self.RDGGS.cell_from_point(
                res, (swx - self.VERTEX_OFFT, swy - self.VERTEX_OFFT), plane=False
            )
        )
        return cl

    def __get_dart_neighbors(self, c: Cell, res: int) -> List[Cell]:
        """_summary_

        Args:
            c (Cell): _description_
            res (int): _description_

        Returns:
            List[Cell]: _description_
        """
        c = self.__reduce(c, res)
        cl: list[Cell] = []
        vert = c.vertices(plane=False, trim_dart=True)
        if c.region() == "north_polar":
            n, se, _ = vert
            cl.append(
                self.RDGGS.cell_from_point(
                    res, (n[0], n[1] + self.VERTEX_OFFT), plane=False
                )
            )
            cl.append(
                self.RDGGS.cell_from_point(
                    res, (n[0], se[1] - self.VERTEX_OFFT), plane=False
                )
            )
        else:
            nw, _, s = vert
            cl.append(
                self.RDGGS.cell_from_point(
                    res, (s[0], s[1] - self.VERTEX_OFFT), plane=False
                )
            )
            cl.append(
                self.RDGGS.cell_from_point(
                    res, (s[0], nw[1] + self.VERTEX_OFFT), plane=False
                )
            )
        return cl

    def __get_neighbors(self, c: Cell, res: int) -> List[Cell]:
        """_summary_

        Args:
            c (Cell): _description_
            size (int): _description_

        Returns:
            List[Cell]: _description_
        """
        c = self.__reduce(c, res)
        nd: dict[str, Cell] = c.neighbors(plane=False)
        cl = list(nd.values())
        shape = c.ellipsoidal_shape()
        if shape == "quad" or shape == "skew_quad":
            cl.extend(self.__get_quad_neighbors(c, res))
        elif shape == "dart":
            cl.extend(self.__get_dart_neighbors(c, res))
        return cl

    def __return(self, cells: List[Cell]) -> List[str]:
        """Return cells as str ids in RESOLUTION.

        Args:
            data (List[Cell]): List of cells.

        Returns:
            List[str]: List of cells in DEFAULT_RES.
        """
        # Return cells in RESOLUTION.
        # Handle both cases resolution>RESOLUTION and resolution<RESOLUTION.
        if cells[0].resolution < self.resolution:
            # return subcells for cells
            cell_list = []
            for cell in cells:
                sub_list = list(cell.subcells(resolution=self.resolution))
                cell_list.extend([str(c) for c in sub_list])
            return cell_list
        elif cells[0].resolution > self.resolution:
            # return parent cells
            diff = cells[0].resolution - self.resolution
            parents = dict.fromkeys([c.suid[0:-diff] for c in cells])
            return [str(c) for c in [Cell(rdggs=self.RDGGS, suid=p) for p in parents]]
        else:
            # return as is
            return [str(c) for c in cells]

    def __get_cells(
        self, cell: Cell, res: int = DEFAULT_RESOLUTION, include_neighbors: bool = True
    ) -> List[str]:
        """Get cells at resolution RESOLUTION.
        Neighbors are calculated at resolution `res`.

        Args:
            cell (str): cell id
            res (int, optional): 0 <= res <= RESOLUTION. Defaults to RESOLUTION.

        Returns:
            List[str]: cell ids at RESOLUTION.
        """
        assert (
            0 <= res <= self.resolution
        ), f"Resolution must satisfy 0 <= res <= {self.resolution}."
        result = [cell]
        if include_neighbors:
            result.extend(self.__get_neighbors(cell, res))
        return self.__return(result)

    def get_cell(self, str_cell: str, res: int = DEFAULT_RESOLUTION) -> Cell:
        return self.RDGGS.cell(suid=self.__str2id(str_cell))

    def get_cells(
        self,
        str_cell: str,
        res: int = DEFAULT_RESOLUTION,
        include_neighbors: bool = True,
    ) -> List[str]:
        """Get cells at resolution RESOLUTION.
        Neighbors are calculated at resolution `res`.

        Args:
            cell (str): cell id
            res (int, optional): 0 <= res <= RESOLUTION. Defaults to RESOLUTION.

        Returns:
            List[str]: cell ids at RESOLUTION.
        """
        assert (
            0 <= res <= self.resolution
        ), f"Resolution must satisfy 0 <= res <= {self.resolution}."
        cell = self.RDGGS.cell(suid=self.__str2id(str_cell))
        return self.__get_cells(cell, res=res, include_neighbors=include_neighbors)

    def lat_lon_to_cells(
        self,
        lat: float,
        lon: float,
        res: int = DEFAULT_RESOLUTION,
        include_neighbors: bool = True,
    ) -> List[str]:
        """Get gdds cell[s] at latitude and longitude.
        see: get_cells()

            Do query with the resolution res.
            NOTE: Will always return cells at resolution RESOLUTION. Be careful.
        Args:
            lat (float): latitude
            lon (float): longitude
            res (int, optional): Resolution 0 <= res <= RESOLUTION. Defaults to RESOLUTION.

        Returns:
            List[str]: cell ids
        """

        cell = self.RDGGS.cell_from_point(res, (lon, lat), plane=False)
        return self.__get_cells(cell, res=res, include_neighbors=include_neighbors)

    def cell_to_lat_lon_rad(self, str_cell: str) -> tuple[float, float, float]:
        cell = self.RDGGS.cell(suid=self.__str2id(str_cell))
        clon, clat = cell.centroid(plane=False)
        points = cell.vertices(plane=False)
        radius = 0
        for plon, plat in points:
            d = haversine((clat, clon), (plat, plon), unit=Unit.METERS)
            if radius < d:
                radius = d + RAD_MARGIN

        return float(clat), float(clon), radius


__all__ = ("Dggs",)
