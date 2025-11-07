from urllib.parse import urlparse, urlunparse

from astropy.time import Time  # type: ignore[import-untyped]
from fastapi import APIRouter, Depends, Query, Request, Response

from ..base.api import app
from ..constants import OBJOBSSAP_DEFAULT_LENGTH, VO_SERVER
from .schema import VOPosition, VOTimeRange
from .service import ObjObsSAPService

router = APIRouter(prefix="/objobssap", tags=["ObjObsSAP"])


def parse_pos(pos: str = Query(..., description="Position in 'RA,DEC' format")) -> VOPosition:
    """Parses the position string into a VOPosition object."""
    return VOPosition.from_string(pos)


def parse_time(
    time: str | None = Query(
        default=None,
        description=(
            "Time range in 'T_MIN/T_MAX' format. Defaults to current date"
            " through 7 days from now if not provided."
        ),
    ),
) -> VOTimeRange:
    """Parses the time string into a VOTimeRange object."""
    if time is None:
        now = Time.now().mjd
        time = f"{now}/{now + OBJOBSSAP_DEFAULT_LENGTH}"
    return VOTimeRange.from_string(time)


def parse_min_obs(min_obs: float = Query(default=0, description="Minimum observation threshold")) -> float:
    """Parses the minimum observation threshold."""
    return float(min_obs)


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
async def objvissap(
    request: Request,
    position: VOPosition = Depends(parse_pos),
    time: VOTimeRange = Depends(parse_time),
    min_obs: float = Depends(parse_min_obs),
    maxrec: int | None = Query(default=None, description="Maximum number of records to return"),
    upload: str | None = Query(
        default=None, description="Not used for ObjObsSAP, but included for consistency"
    ),
):
    """Handles the query for ObjObjSAP."""
    vo = ObjObsSAPService(
        s_ra=position.s_ra,
        s_dec=position.s_dec,
        t_min=time.t_min,
        t_max=time.t_max,
        min_obs=min_obs,
        maxrec=maxrec,
        upload=upload,
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
