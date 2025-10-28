import re
from datetime import UTC, datetime
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

    def __init__(self, s_ra, s_dec, t_min, t_max, min_obs, maxrec=None, upload=None):
        """
        This method initializes the service class.
        """
        self.s_ra = s_ra
        self.s_dec = s_dec
        self.t_min = Time(t_min, format="mjd").datetime
        self.t_max = Time(t_max, format="mjd").datetime
        self.min_obs = min_obs
        self.maxrec = maxrec
        self.upload = upload
        self.windows = []

    async def query(self):
        """
        This method queries the ObjObsSAP service.
        """
        if self.maxrec != 0:
            vis_windows = await asyncify(VisQuery)(
                ra=self.s_ra, dec=self.s_dec, begin=self.t_min, end=self.t_max, hires=True
            )
            self.windows = [
                (Time(e.begin).mjd, Time(e.end).mjd)
                for e in vis_windows.entries
                if e.length.total_seconds() >= self.min_obs
            ]
        if self.maxrec is not None:
            self.windows = self.windows[: self.maxrec]

    async def vo_format(self, query_url: str = "") -> str:
        """
        This method formats the query results into a VOTable using astropy's
        VOTable support.

        Note that this output does match the example in the VO ObjObsSAP 1.0
        documentation (https://www.ivoa.net/documents/ObjObsSAP/), as elements
        have "ID=" attributes not present in the example. This is because the
        VOTable library automatically generates these attributes.
        """

        # Get the current date/time in UTC for the REQUEST_DATE info
        now_utc: datetime = datetime.now(tz=UTC)
        request_date_string: str = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

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

        service_protocol_info = Info(name="SERVICE_PROTOCOL", value="ivo://ivoa.net/std/ObjObsSAP")
        resource.infos.append(service_protocol_info)

        resource.infos.append(Info(name="REQUEST", value=query_url))
        resource.infos.append(
            Info(name="REQUEST_DATE", value=request_date_string, content="Query execution date")
        )

        resource.infos.append(Info(name="POS", value=f"{self.s_ra},{self.s_dec}"))
        resource.infos.append(Info(name="TIME", value=f"{Time(self.t_min).mjd}/{Time(self.t_max).mjd}"))
        if self.min_obs is not None and self.min_obs > 0:
            resource.infos.append(Info(name="MIN_OBS", value=str(self.min_obs)))
        if self.maxrec is not None:
            resource.infos.append(Info(name="MAXREC", value=str(self.maxrec)))
        if self.upload is not None:
            resource.infos.append(Info(name="UPLOAD", value=str(self.upload)))

        # Define the table
        table.fields.extend(
            [
                Field(
                    votable,
                    name="t_validity",
                    datatype="double",
                    ucd="time.validity",
                    utype="Char.TimeAxis.Coverage.Time",
                    unit="d",
                ),
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
                    name="t_observability",
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
            t_start = self.windows[i][0]
            t_stop = self.windows[i][1]
            t_validity = self.windows[0][0] + 10
            t_observability = t_stop - t_start  # Duration in days
            table.array[i] = (
                t_validity,
                t_start,
                t_stop,
                t_observability * 86400,  # t_observability in seconds
            )

        # Create the VOTable XML as a string and return it
        with BytesIO() as stream:
            votable.to_xml(stream)
            stream.seek(0)
            xml_out = stream.read().decode()

        return re.sub(r'(value="[^"]*?)&amp;([^"]*?")', r"\1&\2", xml_out)
