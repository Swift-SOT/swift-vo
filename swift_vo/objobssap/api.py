from urllib.parse import urlparse, urlunparse

from astropy.time import Time  # type: ignore[import-untyped]
from fastapi import APIRouter, Depends, Query, Request, Response

from ..base.api import app
from ..constants import OBJOBSSAP_DEFAULT_LENGTH, VO_ROOT_PATH, VO_SERVER
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
        TIME = f"{now}/{now + OBJOBSSAP_DEFAULT_LENGTH}"
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
    request: Request,
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


@router.get(
    "/capabilities",
    response_class=Response,
    responses={
        200: {
            "content": {
                "application/xml": {
                    "example": '<?xml version="1.0" encoding="UTF-8"?>'
                    "<vosi:capabilities>...</vosi:capabilities>"
                }
            },
            "description": "Returns VOSI capabilities document",
        }
    },
)
async def capabilities():
    """Returns the VOSI capabilities document for ObjObsSAP service."""
    base_url = f"https://{VO_SERVER}{VO_ROOT_PATH}/objobssap"

    capabilities_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<vosi:capabilities
    xmlns:vosi="http://www.ivoa.net/xml/VOSICapabilities/v1.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:vs="http://www.ivoa.net/xml/VODataService/v1.1">
    <capability standardID="ivo://ivoa.net/std/VOSI#capabilities">
        <interface xsi:type="vs:ParamHTTP" version="1.0">
            <accessURL use="base">
                {base_url}/capabilities
            </accessURL>
        </interface>
    </capability>
    <capability standardID="ivo://ivoa.net/std/VOSI#availability">
        <interface xsi:type="vs:ParamHTTP" version="1.0">
            <accessURL use="full">
                {base_url}/availability
            </accessURL>
        </interface>
    </capability>
    <capability standardID="ivo://ivoa.net/std/ObjObsSAP#query-0.3">
        <interface xsi:type="vs:ParamHTTP" role="std" version="0.3">
            <accessURL>
                {base_url}/query
            </accessURL>
        </interface>
    </capability>
</vosi:capabilities>"""

    return Response(content=capabilities_xml, media_type="application/xml")


@router.get(
    "/availability",
    response_class=Response,
    responses={
        200: {
            "content": {
                "application/xml": {
                    "example": '<?xml version="1.0" encoding="UTF-8"?>'
                    "<vosi:availability>...</vosi:availability>"
                }
            },
            "description": "Returns VOSI availability document",
        }
    },
)
async def availability():
    """Returns the VOSI availability document for ObjObsSAP service."""
    availability_xml = """<?xml version="1.0" encoding="UTF-8"?>
<vosi:availability
    xmlns:vosi="http://www.ivoa.net/xml/VOSIAvailability/v1.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <vosi:available>true</vosi:available>
</vosi:availability>"""

    return Response(content=availability_xml, media_type="application/xml")


app.include_router(router)
