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
from swifttools.swift_too import PlanQuery  # type: ignore[import-untyped]


class ObsLocTAPService:
    """
    This class is the service class for the ObsLocTAP service.
    Implements a simple cone search for planned Swift observations.
    """

    def __init__(self, s_ra, s_dec, s_radius, t_min, t_max, maxrec=None):
        """
        Initialize the ObsLocTAP service.

        Parameters
        ----------
        s_ra : float
            Right Ascension in degrees
        s_dec : float
            Declination in degrees
        s_radius : float
            Search radius in degrees
        t_min : float
            Start time in MJD
        t_max : float
            End time in MJD
        maxrec : int, optional
            Maximum number of records to return
        """
        self.s_ra = s_ra
        self.s_dec = s_dec
        self.s_radius = s_radius
        self.t_min = Time(t_min, format="mjd").datetime
        self.t_max = Time(t_max, format="mjd").datetime
        self.maxrec = maxrec
        self.observations = []

    async def query(self):
        """
        Query the Swift Pre-Planned Science Timeline for observations.
        """
        if self.maxrec != 0:
            plan_query = await asyncify(PlanQuery)(
                ra=self.s_ra,
                dec=self.s_dec,
                radius=self.s_radius,
                begin=self.t_min,
                end=self.t_max,
            )
            self.observations = plan_query.entries

        if self.maxrec is not None and len(self.observations) > self.maxrec:
            self.observations = self.observations[: self.maxrec]

    async def vo_format(self, query_url: str = "") -> str:
        """
        Format the query results into a VOTable following ObsLocTAP standard.

        Parameters
        ----------
        query_url : str
            The URL used to make the query

        Returns
        -------
        str
            XML string in VOTable format
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
            + "Observatory Locator Table Access Protocol (ObsLocTAP)"
        )
        resource.infos.append(Info(name="QUERY_STATUS", value="OK"))

        service_protocol_info = Info(name="SERVICE_PROTOCOL", value="ivo://ivoa.net/std/ObsLocTAP")
        resource.infos.append(service_protocol_info)

        resource.infos.append(Info(name="REQUEST", value=query_url))
        resource.infos.append(
            Info(name="REQUEST_DATE", value=request_date_string, content="Query execution date")
        )

        resource.infos.append(Info(name="POS", value=f"{self.s_ra},{self.s_dec},{self.s_radius}"))
        resource.infos.append(Info(name="TIME", value=f"{Time(self.t_min).mjd}/{Time(self.t_max).mjd}"))
        if self.maxrec is not None:
            resource.infos.append(Info(name="MAXREC", value=str(self.maxrec)))

        # Define the table fields according to ObsLocTAP specification
        table.fields.extend(
            [
                Field(
                    votable,
                    name="obs_id",
                    datatype="char",
                    arraysize="*",
                    ucd="meta.id;obs",
                ),
                Field(
                    votable,
                    name="s_ra",
                    datatype="double",
                    ucd="pos.eq.ra",
                    unit="deg",
                ),
                Field(
                    votable,
                    name="s_dec",
                    datatype="double",
                    ucd="pos.eq.dec",
                    unit="deg",
                ),
                Field(
                    votable,
                    name="t_planning",
                    datatype="double",
                    ucd="time.epoch",
                    unit="d",
                ),
                Field(
                    votable,
                    name="t_start",
                    datatype="double",
                    ucd="time.start",
                    unit="d",
                ),
                Field(
                    votable,
                    name="t_stop",
                    datatype="double",
                    ucd="time.end",
                    unit="d",
                ),
                Field(
                    votable,
                    name="target_name",
                    datatype="char",
                    arraysize="*",
                    ucd="meta.id;src",
                ),
            ]
        )

        # Add observations to the table
        n_observations = len(self.observations)
        table.create_arrays(n_observations)
        # For t_planning, we use the current time as the planning time (calculated once)
        t_planning_mjd = Time.now().mjd
        
        for i, obs in enumerate(self.observations):
            t_start_mjd = Time(obs.begin).mjd
            t_stop_mjd = Time(obs.end).mjd

            table.array[i] = (
                str(obs.obsnum) if hasattr(obs, "obsnum") else f"obs_{i}",
                obs.ra if hasattr(obs, "ra") else self.s_ra,
                obs.dec if hasattr(obs, "dec") else self.s_dec,
                t_planning_mjd,
                t_start_mjd,
                t_stop_mjd,
                obs.target_name if hasattr(obs, "target_name") else "Unknown",
            )

        # Create the VOTable XML as a string and return it
        with BytesIO() as stream:
            votable.to_xml(stream)
            stream.seek(0)
            xml_out = stream.read().decode()

        return xml_out
