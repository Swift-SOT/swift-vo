"""VOSI-availability API endpoint implementation."""

from datetime import UTC, datetime

from fastapi import APIRouter, Response
from vo_models.voresource.models import AccessURL, Capability, Interface
from vo_models.vosi.availability import Availability
from vo_models.vosi.capabilities import VOSICapabilities

from ..base.api import app
from ..constants import VO_ROOT_PATH, VO_SERVER

router = APIRouter(prefix="", tags=["VOSI"])

# Store the service startup time at module initialization
SERVICE_STARTUP_TIME = datetime.now(UTC)


@router.get(
    "/objobssap/availability",
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
    xml_content = Availability(available=True, up_since=SERVICE_STARTUP_TIME).to_xml(
        encoding="UTF-8", xml_declaration=True
    )
    return Response(content=xml_content, media_type="application/xml")


@router.get(
    "/objobssap/capabilities",
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
    base_url = f"https://{VO_SERVER}{VO_ROOT_PATH}"

    capabilities = VOSICapabilities(
        capability=[
            Capability(
                standard_id="ivo://ivoa.net/std/VOSI#capabilities",
                interface=[
                    Interface(
                        access_url=[AccessURL(value=f"{base_url}/objobssap/capabilities", use="full")],
                        use="base",
                        version="1.0",
                    )
                ],
            ),
            Capability(
                standard_id="ivo://ivoa.net/std/VOSI#availability",
                interface=[
                    Interface(
                        access_url=[AccessURL(value=f"{base_url}/objobssap/availability", use="full")],
                        version="1.0",
                    )
                ],
            ),
            Capability(
                standard_id="ivo://ivoa.net/std/ObjObsSAP#query-1",
                interface=[
                    Interface(
                        access_url=[AccessURL(value=f"{base_url}/objobssap/query", use="full")],
                        role="std",
                        version="1.0",
                    )
                ],
            ),
        ]
    )

    return Response(
        content=capabilities.to_xml(encoding="UTF-8", xml_declaration=True), media_type="application/xml"
    )


app.include_router(router)
