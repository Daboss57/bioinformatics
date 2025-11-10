"""Tests for asset ingestion endpoints."""

from __future__ import annotations

from datetime import datetime, timezone


def test_vcf_ingest_round_trip(client) -> None:
    payload = {
        "source": "data/variants/example.vcf",
        "records": 3,
        "samples": ["SAMPLE1", "SAMPLE2"],
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "gfa_stats": {"segments": 10, "links": 15},
    }

    response = client.post("/api/v1/assets/vcf", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()

    assert data["source"] == payload["source"]
    assert data["records"] == payload["records"]
    assert data["samples"] == payload["samples"]
    assert data["gfa_stats"] == payload["gfa_stats"]
    assert "id" in data
    assert "ingested_at" in data

    list_response = client.get("/api/v1/assets/vcf")
    assert list_response.status_code == 200
    records = list_response.json()
    assert len(records) == 1
    assert records[0]["id"] == data["id"]