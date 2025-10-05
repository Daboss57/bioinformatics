"""Smoke tests for the PGIP FastAPI application."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_plugins_returns_sample_manifest() -> None:
    response = client.get("/api/v1/plugins/")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload[0]["name"] == "frequency-aggregator"


def test_plugin_404_when_missing() -> None:
    response = client.get("/api/v1/plugins/does-not-exist")
    assert response.status_code == 404
