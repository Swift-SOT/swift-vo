from astropy.time import Time  # type: ignore[import-untyped]
from fastapi import APIRouter, Depends, Query, Response

from ..base.api import app
from .schema import VOPosition, VOTimeRange
from .service import ObjObsSAPService

router = APIRouter(prefix="/objobssap", tags=["ObjObsSAP"])


def parse_pos(POS: str = Query(..., description="Position in 'RA,DEC' format")) -> VOPosition:
    """Parses the position string into a VOPosition object."""
    return VOPosition.from_string(POS)


def parse_time(
    TIME: str | None = Query(
        default=None,
        description=(
            "Time range in 'T_MIN/T_MAX' format. Defaults to current date through"
            " 7 days from now if not provided."
        ),
    ),
) -> VOTimeRange:
    """Parses the time string into a VOTimeRange object."""
    if TIME is None:
        now = Time.now().mjd
        TIME = f"{now}/{now + 7}"
    return VOTimeRange.from_string(TIME)


def parse_min_obs(MIN_OBS: float = Query(default=0, description="Minimum observation threshold")) -> float:
    """Parses the minimum observation threshold."""
    return float(MIN_OBS)


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
    position: VOPosition = Depends(parse_pos),
    time: VOTimeRange = Depends(parse_time),
    min_obs: float = Depends(parse_min_obs),
    MAXREC: int | None = Query(default=None, description="Maximum number of records to return"),
    UPLOAD: str | None = Query(
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
        maxrec=MAXREC,
        upload=UPLOAD,
    )
    await vo.query()
    xml_data = await vo.vo_format()

    return Response(content=xml_data, media_type="application/x-votable+xml")


app.include_router(router)
