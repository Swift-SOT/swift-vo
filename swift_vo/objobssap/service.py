from astropy.time import Time  # type: ignore[import-untyped]
from swifttools.swift_too import VisQuery  # type: ignore[import-untyped]


class ObjObsSAPService:
    """
    This class is the service class for the ObjObsSAP service.
    """

    def __init__(self, s_ra, s_dec, t_min, t_max):
        self.s_ra = s_ra
        self.s_dec = s_dec
        self.t_min = Time(t_min, format="mjd").datetime
        self.t_max = Time(t_max, format="mjd").datetime
        self.windows = []

    def query(self):
        """
        This method queries the ObjObsSAP service.
        """
        vis_windows = VisQuery(self.s_ra, self.s_dec, self.t_min, self.t_max).query()
        self.windows = [(Time(e.begin).mjd, Time(e.end).mjd) for e in vis_windows.entries]
