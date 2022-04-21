from fastapi import FastAPI, Request
from routers.v1 import search_routers, filter_routes, metadata_routes
from keys import redis_keys
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, storage_uri=redis_keys["uri"])

tags_metadata = [
    {
        "name": "search",
        "description": "Searches LibraryGenesis for the given query and returns the books that match."
    },
    {
        "name": "filter",
        "description": "Filters the given books using the given parameters"
    },
    {
        "name": "metadata",
        "description": "Returns either a cover link, or metadata (which includes download links and description) for "
                       "the given md5 and topic."
    },
    {
        "name": "user",
        "description": "Defines methods for populating the user library. Not yet implemented."
    }
]

app = FastAPI(
    title="Biblioterra",
    version="1.0.0",
    openapi_url="/v1/openapi.json",
    docs_url="/v1/docs",
    redoc_url="/v1/redocs",
    openapi_tags=tags_metadata
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(search_routers.router)
app.include_router(filter_routes.router)
app.include_router(metadata_routes.router)


@app.get("/")
@limiter.limit("1/minute")
async def root(request: Request):
    return "See /v1/docs for usage."
