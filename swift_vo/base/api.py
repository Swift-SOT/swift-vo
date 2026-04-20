from urllib.parse import parse_qsl, urlencode

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from .. import __version__  # type: ignore
from ..constants import VO_ROOT_PATH

app = FastAPI(
    title="Swift VO",
    summary="Providing VO services for the Swift Observatory",
    contact={
        "name": "Jamie Kennea",
        "email": "jak51@psu.edu",
    },
    root_path=VO_ROOT_PATH,
    version=__version__,
)


def _normalize_query_string(query_string: bytes) -> bytes:
    """Lowercase query parameter names while preserving their values."""
    if not query_string:
        return query_string

    normalized_items = [
        (key.lower(), value)
        for key, value in parse_qsl(query_string.decode("latin-1"), keep_blank_values=True)
    ]
    return urlencode(normalized_items, doseq=True).encode("latin-1")


class CaseInsensitiveMiddleware(BaseHTTPMiddleware):
    """
    Middleware to convert all request paths to lowercase.
    This is useful for ensuring that all paths are treated uniformly,
    regardless of how they are requested.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Dispatch the request and convert the path to lowercase.
        """
        request.scope["path"] = request.scope["path"].lower()
        request.scope["query_string"] = _normalize_query_string(request.scope.get("query_string", b""))
        response = await call_next(request)
        return response


app.add_middleware(CaseInsensitiveMiddleware)
