"""FastAPI application entrypoint for PGIP."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import assets as assets_routes
from app.api.routes import health as health_routes
from app.api.routes import plugins as plugins_routes
from app.core.config import get_settings
from app.db.session import create_all, get_engine, get_session_factory, init_engine
from app.repositories import plugins as plugin_repo

settings = get_settings()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize and tear down shared resources for the application."""

    init_engine()
    await create_all()

    if settings.seed_demo_data:
        session_factory = get_session_factory()
        async with session_factory() as session:
            inserted = await plugin_repo.seed_demo_plugins(session)
        if inserted:
            logger.info("Seeded %d demo plugin(s) into registry", inserted)

    try:
        yield
    finally:
        try:
            engine = get_engine()
        except RuntimeError:  # pragma: no cover - defensive guard
            return

        await engine.dispose()


app = FastAPI(
    title=settings.project_name,
    description=settings.description,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
    lifespan=lifespan,
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
app.include_router(assets_routes.router, prefix=settings.api_v1_prefix)


@app.get("/", summary="Service metadata")
def read_root() -> dict[str, str]:
    """Return basic metadata about the service."""

    return {"service": settings.project_name, "version": "0.1.0"}
