"""Pytest fixtures for backend tests."""

from __future__ import annotations

import asyncio
import os
from collections.abc import Iterator
from pathlib import Path
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient

from app.db.session import (
    create_all,
    drop_all,
    get_engine,
    get_session,
    get_session_factory,
    init_engine,
)
from app.main import app


@pytest.fixture()
def client(tmp_path: Path) -> Iterator[TestClient]:
    """Provide a TestClient with an isolated SQLite database."""

    database_path = tmp_path / "test_pgip.db"
    database_url = f"sqlite+aiosqlite:///{database_path.as_posix()}"

    os.environ["PGIP_SEED_DEMO_DATA"] = "0"

    init_engine(database_url, echo=False)

    # Recreate schema for the fresh database
    try:
        asyncio.run(drop_all())
    except Exception:  # pragma: no cover - dropping before creation can raise
        pass
    asyncio.run(create_all())

    session_factory = get_session_factory()

    async def override_get_session() -> AsyncGenerator:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_session, None)
    asyncio.run(get_engine().dispose())
