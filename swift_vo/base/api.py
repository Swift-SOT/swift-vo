from fastapi import FastAPI

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
