import uvicorn
from app.api.main import api_router
from app.core.config import settings
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from shared.logging.logger import get_logger, setup_logger
from starlette.middleware.cors import CORSMiddleware

setup_logger()
logger = get_logger("system")


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="IAC-Migration-Tool",
        version="1.0.0",
        openapi_version="3.1.0",
        routes=app.routes,
        servers=[
            {"url": "http://localhost:8080", "description": "Local Development server"}
        ],
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if settings.ALLOWED_ORIGINS_LIST:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.ALLOWED_ORIGINS_LIST
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)


def run_backend(
    host: str = "localhost",
    port: int = 8080,
    reload: bool = True,
):
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
    )
