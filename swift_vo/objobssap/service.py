from io import BytesIO

from astropy.io.votable.tree import (  # type: ignore[import-untyped]
    Field,
    Info,
    Resource,
    TableElement,
    VOTableFile,
)
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

    async def vo_format(self) -> str:
        """
        This method formats the query results into a VOTable using astropy.
        """

        # Create a new VOTable file
        votable = VOTableFile()

        # Define resources
        resource = Resource()
        votable.resources.append(resource)
        table = TableElement(votable)
        resource.tables.append(table)

        # Describe resources
        resource.description = (
            "NASA Neil Gehrels Swift Observatory Science Operations Center - "
            + "Object Observability Simple Access Protocol (ObjObsSAP)"
        )
        resource.infos.append(Info(name="QUERY_STATUS", value="OK"))

        service_protocol_info = Info(name="SERVICE PROTOCOL", value="1.0")
        service_protocol_info.content = "ObjObsSAP"
        resource.infos.append(service_protocol_info)

        resource.infos.append(Info(name="REQUEST", value="queryData"))
        resource.infos.append(Info(name="s_ra", value=str(self.s_ra)))
        resource.infos.append(Info(name="s_dec", value=str(self.s_dec)))
        resource.infos.append(Info(name="t_min", value=str(self.t_min)))
        resource.infos.append(Info(name="t_max", value=str(self.t_max)))
        if self.min_obs is not None:
            resource.infos.append(Info(name="min_obs", value=str(self.min_obs)))
        if self.max_rec is not None:
            resource.infos.append(Info(name="max_rec", value=str(self.max_rec)))
        if self.upload is not None:
            resource.infos.append(Info(name="UPLOAD", value=str(self.upload)))

        # Define the table
        table.fields.extend(
            [
                Field(
                    votable,
                    name="t_start",
                    datatype="double",
                    ucd="time.start",
                    utype="Char.TimeAxis.Coverage.Bounds.Limits.StartTime",
                    unit="d",
                ),
                Field(
                    votable,
                    name="t_stop",
                    datatype="double",
                    ucd="time.end",
                    utype="Char.TimeAxis.Coverage.Bounds.Limits.StopTime",
                    unit="d",
                ),
                Field(
                    votable,
                    name="t_visibility",
                    datatype="double",
                    ucd="time.duration",
                    utype="Char.TimeAxis.Coverage.Support.Extent",
                    unit="s",
                ),
            ]
        )

        # Add windows to the table
        n_windows = len(self.windows)
        table.create_arrays(n_windows)
        for i in range(0, n_windows):
            table.array[i] = (
                self.windows[i][0],
                self.windows[i][1],
                (self.windows[i][1] - self.windows[i][0]) * 86400,
            )

        # Create the VOTable XML as a string and return it
        with BytesIO() as stream:
            votable.to_xml(stream)
            stream.seek(0)
            xml_out = stream.read().decode()
        return xml_out

    async def vo_format_str(self) -> str:
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
