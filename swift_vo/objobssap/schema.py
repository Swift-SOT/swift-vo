from astropy.time import Time  # type: ignore[import-untyped]
from fastapi import HTTPException
from pydantic import BaseModel, Field


def mjdnow() -> float:
    """Return the current time in MJD."""
    return Time.now().mjd


class VOTimeRange(BaseModel):
    """Time range for the query."""

    t_min: float = Field(default_factory=mjdnow)
    t_max: float

    @classmethod
    def from_string(cls, value: str) -> "VOTimeRange":
        """Parses 'T_MIN,T_MAX' string format into TimeRange object."""
        try:
            tmin, tmax = value.split("/")
            t_min = float(tmin) if tmin else mjdnow()
            t_max = float(tmax)
            return cls(t_min=t_min, t_max=t_max)
        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid time range format: {value}. Expected 'T_MIN/T_MAX' (e.g., '59000/59001').",
            ) from e


class VOPosition(BaseModel):
    """Position in the sky."""

    s_ra: float
    s_dec: float

    @classmethod
    def from_string(cls, value: str) -> "VOPosition":
        """Parses 'RA,DEC' string format into RADEC object."""
        try:
            ra, dec = map(float, value.split(","))
            return cls(s_ra=ra, s_dec=dec)
        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid position format: {value}. Expected 'RA,DEC' (e.g., '34,-23.3').",
            ) from e


class ObjObsSAPQueryParameters(BaseModel):
    """Query parameters for ObjObsSAP."""

    pos: VOPosition
    time: VOTimeRange
    min_obs: float
