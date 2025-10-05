"""FastAPI application entrypoint for PGIP."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health as health_routes
from app.api.routes import plugins as plugins_routes
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    description=settings.description,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_routes.router)
app.include_router(plugins_routes.router, prefix=settings.api_v1_prefix)


@app.get("/", summary="Service metadata")
def read_root() -> dict[str, str]:
    """Return basic metadata about the service."""

    return {"service": settings.project_name, "version": "0.1.0"}
