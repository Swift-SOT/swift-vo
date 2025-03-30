from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from .. import __version__  # type: ignore

app = FastAPI(
    title="Swift VO",
    summary="Providing VO services for the Swift Observatory",
    contact={
        "name": "Jamie Kennea",
        "email": "jak51@psu.edu",
    },
    root_path="/vo",
    version=__version__,
)


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
        # Convert path to lowercase
        request.scope["path"] = request.scope["path"].lower()
        response = await call_next(request)
        return response


app.add_middleware(CaseInsensitiveMiddleware)
