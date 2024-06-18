from typing import List

from rhealpixdggs.dggs import WGS84_ELLIPSOID, Cell, RHEALPixDGGS

RESOLUTION = 8  # Cell area: 2e+5, side: ~1.4km


class Dggs:
    """Dggs helper using RHEALPixDGGS.

    see: https://raichev.net/files/rhealpix_dggs_preprint.pdf
    """

    RDGGS = RHEALPixDGGS(ellipsoid=WGS84_ELLIPSOID)
    VERTEX_OFFT = 0.001

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
        if cells[0].resolution < RESOLUTION:
            # return subcells for cells
            cell_list = []
            for cell in cells:
                sub_list = list(cell.subcells(resolution=RESOLUTION))
                cell_list.extend([str(c) for c in sub_list])
            return cell_list
        elif cells[0].resolution > RESOLUTION:
            # return parent cells
            diff = cells[0].resolution - RESOLUTION
            parents = dict.fromkeys([c.suid[0:-diff] for c in cells])
            return [str(c) for c in [Cell(rdggs=self.RDGGS, suid=p) for p in parents]]
        else:
            # return as is
            return [str(c) for c in cells]

    def __get_cells(
        self, cell: Cell, res: int = RESOLUTION, include_neighbors: bool = True
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
            0 <= res <= RESOLUTION
        ), f"Resolution must satisfy 0 <= res <= {RESOLUTION}."
        result = [cell]
        if include_neighbors:
            result.extend(self.__get_neighbors(cell, res))
        return self.__return(result)

    def get_cells(
        self, str_cell: str, res: int = RESOLUTION, include_neighbors: bool = True
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
            0 <= res <= RESOLUTION
        ), f"Resolution must satisfy 0 <= res <= {RESOLUTION}."
        head = [str_cell[0]]
        tail = [int(e) for e in str_cell[1:]]
        cell = self.RDGGS.cell(head + tail)
        return self.__get_cells(cell, res=res, include_neighbors=include_neighbors)

    def lat_lon_to_cells(
        self,
        lat: float,
        lon: float,
        res: int = RESOLUTION,
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


__all__ = ("Dggs", "RESOLUTION")
