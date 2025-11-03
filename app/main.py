try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

# IMPORTANT: Import all SQLModel models here so they are registered with SQLAlchemy
# This ensures relationships and foreign keys are properly configured before any DB operations
from app.auth.models import Role, User, UserRole  # noqa

from app.api.main import api_router
from app.config.config import settings
from app.config.response import error_response


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if SENTRY_AVAILABLE and settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set CORS only if origins are configured
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


# Exception handlers for standard response format
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler for HTTPException to return standard response format.
    """
    response, status_code = error_response(
        message=exc.detail,
        status_code=exc.status_code,
    )
    return JSONResponse(
        content=response.model_dump(),
        status_code=status_code,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for general exceptions to return standard response format.
    """
    response, status_code = error_response(
        message="Internal server error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    return JSONResponse(
        content=response.model_dump(),
        status_code=status_code,
    )
