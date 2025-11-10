"""Plugin discovery endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.plugin import PluginManifest, PluginStats, PluginSummary
from app.repositories import plugins as plugin_repo

router = APIRouter(prefix="/plugins", tags=["plugins"])


@router.get("/", response_model=list[PluginSummary])
async def list_plugins(
    session: AsyncSession = Depends(get_session),
) -> list[PluginSummary]:
    """Return a collection of available plugins."""

    records = await plugin_repo.list_plugins(session)
    return [
        PluginSummary(
            name=record.name,
            version=record.version,
            description=record.description,
            tags=record.tags or [],
            latest_run_at=record.latest_run_at,
        )
        for record in records
    ]


@router.get("/stats", response_model=PluginStats)
async def get_plugin_stats(
    session: AsyncSession = Depends(get_session),
) -> PluginStats:
    """Return aggregate statistics for the plugin registry."""

    return await plugin_repo.get_plugin_stats(session)


@router.get("/{plugin_name}", response_model=PluginManifest)
async def get_plugin(
    plugin_name: str,
    version: str | None = Query(default=None, description="Specific plugin version to fetch"),
    session: AsyncSession = Depends(get_session),
) -> PluginManifest:
    """Return the manifest for a specific plugin."""

    record = await plugin_repo.get_plugin(session, name=plugin_name, version=version)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plugin not found")
    return PluginManifest.model_validate(record.manifest)


@router.post("/", response_model=PluginManifest, status_code=status.HTTP_201_CREATED)
async def register_plugin(
    manifest: PluginManifest,
    session: AsyncSession = Depends(get_session),
) -> PluginManifest:
    """Create or update a plugin manifest."""

    record = await plugin_repo.upsert_plugin(session, manifest)
    return PluginManifest.model_validate(record.manifest)


@router.delete("/{plugin_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plugin(
    plugin_name: str,
    version: str = Query(..., description="Plugin version to delete"),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a plugin manifest."""

    success = await plugin_repo.delete_plugin(session, name=plugin_name, version=version)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plugin not found")
