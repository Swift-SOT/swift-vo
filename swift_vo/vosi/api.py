"""VOSI-availability API endpoint implementation."""

from datetime import UTC, datetime

from fastapi import APIRouter, Response

from swift_vo.constants import VO_ROOT_PATH, VO_SERVER

from ..base.api import app

router = APIRouter(prefix="", tags=["VOSI"])

# Store the service startup time at module initialization
SERVICE_STARTUP_TIME = datetime.now(UTC).isoformat()


@router.get(
    "/availability",
    response_class=Response,
    responses={
        200: {
            "content": {
                "application/xml": {
                    "example": """<?xml version="1.0" encoding="UTF-8"?>
<availability xmlns="http://www.ivoa.net/xml/VOSIAvailability/v1.0">
    <available>true</available>
</availability>"""
                }
            },
            "description": "Returns VOSI availability status",
        }
    },
)
async def availability() -> Response:
    """
    VOSI-availability endpoint.

    Returns the availability status of the service as required by DALI and ObjObsSAP specifications.
    The endpoint follows IVOA VOSI (Virtual Observatory Support Interfaces) standard.
    """
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<availability xmlns="http://www.ivoa.net/xml/VOSIAvailability/v1.0"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <available>true</available>
    <upSince>{SERVICE_STARTUP_TIME}</upSince>
</availability>"""

    return Response(content=xml_content, media_type="application/xml")


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


app.include_router(router)
