from astropy.time import Time  # type: ignore[import-untyped]
from asyncer import asyncify
from swifttools.swift_too import VisQuery  # type: ignore[import-untyped]


class ObjObsSAPService:
    """
    This class is the service class for the ObjObsSAP service.
    """

    def __init__(self, s_ra, s_dec, t_min, t_max, min_obs, max_rec=None, upload=None):
        """
        This method initializes the service class.
        """
        self.s_ra = s_ra
        self.s_dec = s_dec
        self.t_min = Time(t_min, format="mjd").datetime
        self.t_max = Time(t_max, format="mjd").datetime
        self.min_obs = min_obs
        self.max_rec = max_rec
        self.upload = upload
        self.windows = []

    async def query(self):
        """
        This method queries the ObjObsSAP service.
        """
        if self.max_rec != 0:
            vis_windows = await asyncify(VisQuery)(
                ra=self.s_ra, dec=self.s_dec, begin=self.t_min, end=self.t_max, hires=True
            )
            self.windows = [
                (Time(e.begin).mjd, Time(e.end).mjd)
                for e in vis_windows.entries
                if e.length.total_seconds() >= self.min_obs
            ]
        if self.max_rec is not None:
            self.windows = self.windows[: self.max_rec]

    async def vo_format(self):
        """
        This method formats the query results into a VOTable.
        """
        vo = f"""<?xml version="1.0" encoding="UTF-8"?>
<VOTABLE xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:noNamespaceSchemaLocation="
xmlns:http://www.ivoa.net/xml/VOTable/VOTable-1.1.xsd"
xmlns:ssldm="http://www.ivoa.net/xml/ObjectObservabilityDM/ObjectObservabilityDM-v1.0.xsd"
version="1.0">
<RESOURCE type="results">
<DESCRIPTION>
NASA Neil Gehrels Swift Observatory Science Operations Center -
Object Observability Simple Access Protocol (ObjObsSAP)
</DESCRIPTION>
<INFO name="QUERY_STATUS" value="OK"/>
<INFO name="SERVICE PROTOCOL" value="1.0">
ObjObsSAP
</INFO>
<INFO name="POS" value="{self.s_ra},{self.s_dec}"/>
<INFO name="TIME" value="{Time(self.t_min).mjd}/{Time(self.t_max).mjd}"/>
<TABLE>
<FIELD name="t_start" ucd="time.start"
utype="Char.TimeAxis.Coverage.Bounds.Limits.StartTime"
datatype="float" unit="d"/>
<FIELD name="t_stop" ucd="time.end"
utype="Char.TimeAxis.Coverage.Bounds.Limits.StopTime"
datatype="float" unit="d"/>
<FIELD name="t_observability"
utype="Char.TimeAxis.Coverage.Support.Extent"
ucd="time.duration" datatype="float" unit="s"/>\n"""
        if self.max_rec != 0:
            vo += "<DATA>\n"
            vo += "<TABLEDATA>\n"

            for window in self.windows:
                vo += "<TR>\n"
                vo += f"<TD>{window[0]:.5f}</TD>\n"
                vo += f"<TD>{window[1]:.5f}</TD>\n"
                vo += f"<TD>{(window[1] - window[0]) * 86400:.0f}</TD>\n"
                vo += "</TR>\n"

            vo += "</TABLEDATA>\n"
            vo += "</DATA>\n"
        vo += "</TABLE>\n"
        vo += "</RESOURCE>\n"
        vo += "</VOTABLE>\n"

        return vo
