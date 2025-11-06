"""VOSI-availability API endpoint implementation."""

from datetime import UTC, datetime

from fastapi import APIRouter, Response

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
async def availability():
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


app.include_router(router)
