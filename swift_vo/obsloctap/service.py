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
from swifttools.swift_too import ObsQuery, PlanQuery  # type: ignore[import-untyped]


class ObsLocTAPService:
    """
    This class is the service class for the ObsLocTAP service.
    Implements a simple cone search for planned and executed Swift observations.
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
        t_min : float or None
            Start time in MJD, or None for no time filtering
        t_max : float or None
            End time in MJD, or None for no time filtering
        maxrec : int, optional
            Maximum number of records to return
        """
        self.s_ra = s_ra
        self.s_dec = s_dec
        self.s_radius = s_radius
        self.t_min = Time(t_min, format="mjd").datetime if t_min is not None else None
        self.t_max = Time(t_max, format="mjd").datetime if t_max is not None else None
        self.maxrec = maxrec
        self.observations = []

    async def query(self):
        """
        Query the Swift As-Flown Science Timeline and Pre-Planned Science Timeline for observations.

        Retrieves both executed observations (from ObsQuery) and planned observations (from PlanQuery).
        To avoid duplication, only planned observations starting after the most recent executed observation
        are included.
        """
        # First, get executed observations from ObsQuery
        executed_obs = []
        most_recent_exec_time = None

        if self.maxrec != 0:
            query_kwargs = {
                "ra": self.s_ra,
                "dec": self.s_dec,
                "radius": self.s_radius,
            }
            if self.t_min is not None:
                query_kwargs["begin"] = self.t_min
            if self.t_max is not None:
                query_kwargs["end"] = self.t_max
            obs_query = await asyncify(ObsQuery)(**query_kwargs)
            executed_obs = obs_query.entries

            # Track the most recent execution end time to filter planned observations
            if executed_obs:
                most_recent_exec_time = max(Time(obs.end).mjd for obs in executed_obs)

        # Then, get planned observations from PlanQuery
        planned_obs = []
        if self.maxrec != 0:
            query_kwargs = {
                "ra": self.s_ra,
                "dec": self.s_dec,
                "radius": self.s_radius,
            }
            if self.t_min is not None:
                query_kwargs["begin"] = self.t_min
            if self.t_max is not None:
                query_kwargs["end"] = self.t_max
            plan_query = await asyncify(PlanQuery)(**query_kwargs)
            # Filter planned observations: only include those starting after the most recent execution
            if most_recent_exec_time is not None:
                planned_obs = [
                    obs for obs in plan_query.entries if Time(obs.begin).mjd > most_recent_exec_time
                ]
            else:
                planned_obs = plan_query.entries

        # Combine observations: executed first, then planned
        # Each entry is a tuple of (observation, execution_status)
        self.observations = [(obs, "executed") for obs in executed_obs] + [
            (obs, "planned") for obs in planned_obs
        ]

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
            Info(name="REQUEST_DATE", value=request_date_string)
        )

        resource.infos.append(Info(name="POS", value=f"{self.s_ra},{self.s_dec},{self.s_radius}"))
        if self.t_min is not None and self.t_max is not None:
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
                Field(
                    votable,
                    name="execution_status",
                    datatype="char",
                    arraysize="*",
                    ucd="meta.version",
                ),
            ]
        )

        # Add observations to the table
        n_observations = len(self.observations)
        table.create_arrays(n_observations)
        # For t_planning, we use the current time as the planning time (calculated once)
        t_planning_mjd = Time.now().mjd

        for i, (obs, execution_status) in enumerate(self.observations):
            t_start_mjd = Time(obs.begin).mjd
            t_stop_mjd = Time(obs.end).mjd

            table.array[i] = (
                str(obs.obsnum) if hasattr(obs, "obsnum") else f"obs_{i}",
                obs.ra if hasattr(obs, "ra") else self.s_ra,
                obs.dec if hasattr(obs, "dec") else self.s_dec,
                t_planning_mjd,
                t_start_mjd,
                t_stop_mjd,
                obs.targname if hasattr(obs, "targname") else "Unknown",
                execution_status,
            )

        # Create the VOTable XML as a string and return it
        with BytesIO() as stream:
            votable.to_xml(stream)
            stream.seek(0)
            xml_out = stream.read().decode()

        return xml_out
