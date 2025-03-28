from fastapi import APIRouter, Depends, Query

from ..base.api import app
from .schema import VOPosition, VOTimeRange

router = APIRouter(prefix="/objobssap", tags=["ObjObsSAP"])


def parse_pos(POS: str = Query(..., description="Position in 'RA,DEC' format")) -> VOPosition:
    """Parses the position string into a VOPosition object."""
    return VOPosition.from_string(POS)


def parse_time(TIME: str = Query(..., description="Time range in 'T_MIN/T_MAX' format")) -> VOTimeRange:
    """Parses the time string into a VOTimeRange object."""
    return VOTimeRange.from_string(TIME)


@router.get("/query")
async def objvissap(
    position: VOPosition = Depends(parse_pos), time: VOTimeRange = Depends(parse_time)
) -> dict:
    """Handles the query for ObjObjSAP."""
    return {"ra": position.s_ra, "dec": position.s_dec, "t_min": time.t_min, "t_max": time.t_max}


app.include_router(router)
