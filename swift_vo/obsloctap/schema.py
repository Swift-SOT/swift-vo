from __future__ import annotations

from astropy.time import Time  # type: ignore[import-untyped]
from fastapi import HTTPException
from pydantic import BaseModel, Field


def mjdnow() -> float:
    """Return the current time in MJD."""
    return Time.now().mjd


class ObsLocTAPPosition(BaseModel):
    """Position in the sky for cone search."""

    s_ra: float
    s_dec: float
    s_radius: float = Field(default=0.197)  # Default radius in degrees

    @classmethod
    def from_string(cls, value: str) -> ObsLocTAPPosition:
        """Parses 'RA,DEC' or 'RA,DEC,RADIUS' string format into Position object."""
        try:
            parts = value.split(",")
            if len(parts) == 2:
                ra, dec = map(float, parts)
                return cls(s_ra=ra, s_dec=dec)
            elif len(parts) == 3:
                ra, dec, radius = map(float, parts)
                return cls(s_ra=ra, s_dec=dec, s_radius=radius)
            else:
                raise ValueError("Invalid format")
        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid position format: {value}. Expected 'RA,DEC' or 'RA,DEC,RADIUS'.",
            ) from e


class ObsLocTAPTimeRange(BaseModel):
    """Time range for the query."""

    t_min: float = Field(default_factory=mjdnow)
    t_max: float

    @classmethod
    def from_string(cls, value: str) -> ObsLocTAPTimeRange:
        """Parses 'T_MIN/T_MAX' string format into TimeRange object."""
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
