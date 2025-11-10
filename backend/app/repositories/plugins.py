"""Data access helpers for plugins."""

from __future__ import annotations

import json
import logging
from collections import Counter
from pathlib import Path
from typing import Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Plugin
from app.models.plugin import PluginManifest, PluginStats, PluginTagSummary

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_DATA_DIR = PROJECT_ROOT / "data" / "plugins"


async def list_plugins(session: AsyncSession) -> list[Plugin]:
    """Return plugins ordered by most recent update."""

    stmt: Select[tuple[Plugin]] = select(Plugin).order_by(Plugin.updated_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_plugin(
    session: AsyncSession, *, name: str, version: Optional[str] = None
) -> Optional[Plugin]:
    """Fetch a plugin by name and optional version."""

    stmt: Select[tuple[Plugin]] = select(Plugin).where(Plugin.name == name)
    if version:
        stmt = stmt.where(Plugin.version == version)
    else:
        stmt = stmt.order_by(Plugin.updated_at.desc()).limit(1)

    result = await session.execute(stmt)
    return result.scalars().first()


async def upsert_plugin(session: AsyncSession, manifest: PluginManifest) -> Plugin:
    """Insert or update a plugin manifest."""

    plugin = await get_plugin(session, name=manifest.name, version=manifest.version)

    manifest_payload = manifest.model_dump(mode="json")

    if plugin:
        plugin.description = manifest.description
        plugin.entrypoint = manifest.entrypoint
        plugin.authors = manifest.authors
        plugin.tags = manifest.tags
        plugin.manifest = manifest_payload
        plugin.created_at = manifest.created_at
        plugin.updated_at = manifest.updated_at
        plugin.latest_run_at = manifest.updated_at
    else:
        plugin = Plugin(
            name=manifest.name,
            version=manifest.version,
            description=manifest.description,
            entrypoint=manifest.entrypoint,
            authors=list(manifest.authors),
            tags=list(manifest.tags),
            manifest=manifest_payload,
            created_at=manifest.created_at,
            updated_at=manifest.updated_at,
            latest_run_at=manifest.updated_at,
        )
        session.add(plugin)

    await session.commit()
    await session.refresh(plugin)
    return plugin


async def delete_plugin(session: AsyncSession, *, name: str, version: str) -> bool:
    """Delete a plugin by name/version pair."""

    plugin = await get_plugin(session, name=name, version=version)
    if plugin is None:
        return False

    await session.delete(plugin)
    await session.commit()
    return True


async def get_plugin_stats(session: AsyncSession) -> PluginStats:
    """Aggregate registry statistics for dashboard consumption."""

    records = await list_plugins(session)
    if not records:
        return PluginStats(total_plugins=0, unique_authors=0, unique_tags=0)

    tag_counter: Counter[str] = Counter()
    authors: set[str] = set()
    most_recent = None

    for record in records:
        tag_counter.update(record.tags or [])
        authors.update(record.authors or [])
        if most_recent is None or (record.updated_at and record.updated_at > most_recent):
            most_recent = record.updated_at

    top_tags = [
        PluginTagSummary(tag=tag, usage_count=count)
        for tag, count in tag_counter.most_common(5)
    ]

    return PluginStats(
        total_plugins=len(records),
        unique_authors=len(authors),
        unique_tags=len(tag_counter),
        most_recent_update=most_recent,
        top_tags=top_tags,
    )


async def seed_demo_plugins(session: AsyncSession) -> int:
    """Populate the registry with demo plugins if none exist."""

    existing = await list_plugins(session)
    if existing:
        return 0

    inserted = 0
    manifests = _load_manifests_from_disk()
    for manifest in manifests:
        await upsert_plugin(session, manifest)
        inserted += 1
    return inserted


def _load_manifests_from_disk() -> list[PluginManifest]:
    """Read plugin manifests from the data/plugins directory."""

    if not PLUGIN_DATA_DIR.exists():
        LOGGER.warning("Plugin data directory %s not found", PLUGIN_DATA_DIR)
        return []

    manifests: list[PluginManifest] = []
    for manifest_path in sorted(PLUGIN_DATA_DIR.glob("*.json")):
        try:
            payload = json.loads(manifest_path.read_text())
            manifest = PluginManifest.model_validate(payload)
        except Exception as exc:  # pragma: no cover - defensive guard
            LOGGER.error("Failed to load plugin manifest %s: %s", manifest_path, exc)
            continue
        manifests.append(manifest)

    return manifests
