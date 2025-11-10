"""ORM models for PGIP."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


class Plugin(Base):
    """Persistent representation of a plugin manifest."""

    __tablename__ = "plugins"
    __table_args__ = (UniqueConstraint("name", "version", name="uq_plugin_name_version"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    entrypoint: Mapped[str] = mapped_column(String(512))
    authors: Mapped[list[str]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=list)
    tags: Mapped[list[str]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=list)
    manifest: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    latest_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AssetIngest(Base):
    """Captured summary for an ingested dataset asset."""

    __tablename__ = "asset_ingests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_type: Mapped[str] = mapped_column(String(50), index=True)
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    records: Mapped[int] = mapped_column(Integer, nullable=False)
    samples: Mapped[list[str]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=list)
    gfa_stats: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    payload: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
