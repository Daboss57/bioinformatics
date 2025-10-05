"""Health and metadata endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Service heartbeat", description="Basic health probe.")
def get_health() -> dict[str, str]:
    """Return a simple service heartbeat payload."""

    return {"status": "ok"}
