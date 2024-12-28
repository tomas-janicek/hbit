import logging.config

import sentry_sdk
import svcs
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from hbit_api.api.main import api_router
from hbit_api.bootstrap import bootstrap
from hbit_api.core.config import LOGGING, settings

if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


@svcs.fastapi.lifespan
async def lifespan(app: FastAPI, registry: svcs.Registry):
    bootstrap(registry)

    # Yield other initial states of FastAPI
    yield

    # Close all dependencies after the yield.
    # Registry is closed automatically when the app is done.


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/", response_class=RedirectResponse, tags=["docs"])
async def redirect_to_docs() -> str:
    return "/docs"


app.include_router(api_router, prefix=settings.API_V1_STR)


logging.config.dictConfig(config=LOGGING)
