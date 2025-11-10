"""Smoke tests for the PGIP FastAPI application."""

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.models.plugin import PluginManifest


def _sample_manifest() -> dict:
    manifest = PluginManifest(
        name="frequency-aggregator",
        version="0.1.0",
        description="Annotates variants with population allele frequencies from public datasets.",
        authors=["PGIP Core Team"],
        entrypoint="python -m pgip_plugins.frequency_aggregator",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        inputs=[
            {
                "name": "variants",
                "description": "VCF slice to annotate",
                "media_type": "application/vnd.pgip.vcf",
            }
        ],
        outputs=[
            {
                "name": "annotations",
                "description": "Annotation records in JSONL",
                "media_type": "application/vnd.pgip.annotation+jsonl",
            }
        ],
        tags=["frequency", "baseline"],
        provenance={
            "container_image": "ghcr.io/pgip/frequency-aggregator:0.1.0",
            "repository_url": "https://github.com/pgip-dev/plugins",
            "reference": "main",
        },
        resources={"memory": "4Gi", "cpu": "2"},
    )
    return manifest.model_dump(mode="json")


def test_health_endpoint_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_plugin_lifecycle(client: TestClient) -> None:
    manifest_payload = _sample_manifest()

    create_response = client.post("/api/v1/plugins/", json=manifest_payload)
    assert create_response.status_code == 201

    list_response = client.get("/api/v1/plugins/")
    assert list_response.status_code == 200
    plugins = list_response.json()
    assert len(plugins) == 1
    assert plugins[0]["name"] == manifest_payload["name"]

    detail_response = client.get(f"/api/v1/plugins/{manifest_payload['name']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["version"] == manifest_payload["version"]

    delete_response = client.delete(
        f"/api/v1/plugins/{manifest_payload['name']}", params={"version": manifest_payload["version"]}
    )
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/v1/plugins/{manifest_payload['name']}")
    assert missing_response.status_code == 404


def test_delete_missing_plugin_returns_404(client: TestClient) -> None:
    response = client.delete("/api/v1/plugins/unknown", params={"version": "0.0.1"})
    assert response.status_code == 404


def test_plugin_stats_endpoint(client: TestClient) -> None:
    manifest_payload = _sample_manifest()
    manifest_payload["tags"].extend(["frequency", "population"])
    manifest_payload["authors"].append("Guest Scientist")

    create_response = client.post("/api/v1/plugins/", json=manifest_payload)
    assert create_response.status_code == 201

    stats_response = client.get("/api/v1/plugins/stats")
    assert stats_response.status_code == 200
    stats = stats_response.json()

    assert stats["total_plugins"] == 1
    assert stats["unique_authors"] == 2
    assert stats["unique_tags"] >= 2
    assert stats["most_recent_update"] is not None
    assert stats["top_tags"]
    top_tag_names = {tag["tag"] for tag in stats["top_tags"]}
    assert "frequency" in top_tag_names
