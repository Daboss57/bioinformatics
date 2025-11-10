"""Asset ingestion endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.asset import VcfIngestRecord, VcfIngestRequest
from app.repositories import assets as assets_repo

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/vcf", response_model=VcfIngestRecord, status_code=status.HTTP_201_CREATED)
async def ingest_vcf_asset(
    payload: VcfIngestRequest, session: AsyncSession = Depends(get_session)
) -> VcfIngestRecord:
    """Persist an ingest summary emitted by the pipeline."""

    return await assets_repo.record_vcf_ingest(session, payload)


@router.get("/vcf", response_model=list[VcfIngestRecord])
async def list_vcf_ingests(
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    session: AsyncSession = Depends(get_session),
) -> list[VcfIngestRecord]:
    """Return recent ingest summaries for VCF datasets."""

    return await assets_repo.list_recent_vcf_ingests(session, limit=limit)
