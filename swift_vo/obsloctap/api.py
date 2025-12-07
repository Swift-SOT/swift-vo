from urllib.parse import urlparse, urlunparse

from astropy.time import Time  # type: ignore[import-untyped]
from fastapi import APIRouter, Depends, Query, Request, Response

from ..base.api import app
from ..constants import OBJOBSSAP_DEFAULT_LENGTH, VO_SERVER
from .schema import ObsLocTAPPosition, ObsLocTAPTimeRange
from .service import ObsLocTAPService

router = APIRouter(prefix="/obsloctap", tags=["ObsLocTAP"])


def parse_pos(
    pos: str = Query(..., description="Position in 'RA,DEC' or 'RA,DEC,RADIUS' format")
) -> ObsLocTAPPosition:
    """Parses the position string into an ObsLocTAPPosition object."""
    return ObsLocTAPPosition.from_string(pos)


def parse_time(
    time: str | None = Query(
        default=None,
        description=(
            "Time range in 'T_MIN/T_MAX' format. Defaults to current date"
            " through 7 days from now if not provided."
        ),
    ),
) -> ObsLocTAPTimeRange:
    """Parses the time string into an ObsLocTAPTimeRange object."""
    if time is None:
        now = Time.now().mjd
        time = f"{now}/{now + OBJOBSSAP_DEFAULT_LENGTH}"
    return ObsLocTAPTimeRange.from_string(time)


@router.get(
    "/query",
    response_class=Response,
    responses={
        200: {
            "content": {
                "application/x-votable+xml": {
                    "example": "<note><to>User</to><from>Server</from><message>Hello, XML!</message></note>"
                }
            },
            "description": "Returns a VOTable response",
        }
    },
)
async def obsloctap(
    request: Request,
    position: ObsLocTAPPosition = Depends(parse_pos),
    time: ObsLocTAPTimeRange = Depends(parse_time),
    maxrec: int | None = Query(default=None, description="Maximum number of records to return"),
):
    """Handles the query for ObsLocTAP."""
    vo = ObsLocTAPService(
        s_ra=position.s_ra,
        s_dec=position.s_dec,
        s_radius=position.s_radius,
        t_min=time.t_min,
        t_max=time.t_max,
        maxrec=maxrec,
    )
    await vo.query()

    # Ensure the query_url uses the correct base URL
    parsed_url = urlparse(str(request.url))
    fixed_url = urlunparse(
        (
            "https",
            VO_SERVER,
            parsed_url.path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment,
        )
    )

    xml_data = await vo.vo_format(query_url=str(fixed_url))

    return Response(content=xml_data, media_type="application/x-votable+xml")


app.include_router(router)
