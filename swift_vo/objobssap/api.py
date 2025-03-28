from fastapi import APIRouter, Depends, Query, Response

from swift_vo.objobssap.service import ObjObsSAPService

from ..base.api import app
from .schema import VOPosition, VOTimeRange

router = APIRouter(prefix="/objobssap", tags=["ObjObsSAP"])


def parse_pos(POS: str = Query(..., description="Position in 'RA,DEC' format")) -> VOPosition:
    """Parses the position string into a VOPosition object."""
    return VOPosition.from_string(POS)


def parse_time(TIME: str = Query(..., description="Time range in 'T_MIN/T_MAX' format")) -> VOTimeRange:
    """Parses the time string into a VOTimeRange object."""
    return VOTimeRange.from_string(TIME)


def parse_min_obs(MIN_OBS: float = Query(..., description="Minimum observation threshold")) -> float:
    """Parses the minimum observation threshold."""
    return float(MIN_OBS)


@router.get("/query")
async def objvissap(
    position: VOPosition = Depends(parse_pos),
    time: VOTimeRange = Depends(parse_time),
    min_obs: float = Depends(parse_min_obs),
):
    """Handles the query for ObjObjSAP."""
    vo = ObjObsSAPService(
        s_ra=position.s_ra, s_dec=position.s_dec, t_min=time.t_min, t_max=time.t_max, min_obs=min_obs
    )
    vo.query()
    xml_data = vo.vo_format()

    return Response(content=xml_data, media_type="application/xml")


app.include_router(router)
