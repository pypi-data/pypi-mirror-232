"""main.py."""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from strangeworks_core.errors.error import StrangeworksError

from strangeworks_remote_job.app.middleware import RequestContextMiddleware
from strangeworks_remote_job.app.routers import backends, jobs


logging.basicConfig(level=logging.INFO)
gql_logger = logging.getLogger("gql.transport.requests")
gql_logger.setLevel(logging.DEBUG)

app = FastAPI()


@app.exception_handler(StrangeworksError)
async def http_exception_handler(
    request: Request, exc: StrangeworksError
) -> JSONResponse:
    """Exception handler for StrangeworksError exceptions.

    More info on how this works here: https://tinyurl.com/2hfr9fwj

    Parameters
    ----------
    requst: Request
        request object.
    exc: StrangeworksError
        StrangeworksError exception.

    Return
    ------
    :JSONResponse
        The exception represented as a JSONResponse object.
    """
    logging.warning(f"{exc.message}")
    return JSONResponse(status_code=400, content={"error": exc.message})


# add routers
app.add_middleware(RequestContextMiddleware)

app.include_router(backends.router)
app.include_router(jobs.router)
app.include_router(backends.router)
