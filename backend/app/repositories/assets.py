"""Repository helpers for dataset asset ingests."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.models.asset import VcfIngestRecord, VcfIngestRequest


async def record_vcf_ingest(session: AsyncSession, payload: VcfIngestRequest) -> VcfIngestRecord:
    """Persist a VCF ingest summary produced by the pipeline."""

    record = models.AssetIngest(
        asset_type="vcf",
        source_path=payload.source,
        records=payload.records,
        samples=payload.samples,
        gfa_stats=payload.gfa_stats,
        payload=payload.model_dump(mode="json"),
        created_at=payload.created_at,
        ingested_at=datetime.now(timezone.utc),
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return VcfIngestRecord(
        id=record.id,
        source=record.source_path,
        records=record.records,
        samples=record.samples or [],
        gfa_stats=record.gfa_stats,
        created_at=record.created_at,
        ingested_at=record.ingested_at,
    )


async def list_recent_vcf_ingests(session: AsyncSession, limit: int = 10) -> list[VcfIngestRecord]:
    """Return the most recent VCF ingest events."""

    stmt = (
        select(models.AssetIngest)
        .where(models.AssetIngest.asset_type == "vcf")
        .order_by(models.AssetIngest.ingested_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return [
        VcfIngestRecord(
            id=row.id,
            source=row.source_path,
            records=row.records,
            samples=row.samples or [],
            gfa_stats=row.gfa_stats,
            created_at=row.created_at,
            ingested_at=row.ingested_at,
        )
        for row in result.scalars().all()
    ]
