"""Plugin discovery endpoints."""

from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.models.plugin import PluginManifest, PluginSummary

router = APIRouter(prefix="/plugins", tags=["plugins"])

# In lieu of a real database, provide a static example manifest so the
# API surfaces the schema contract from day one.
_SAMPLE_MANIFEST = PluginManifest(
    name="frequency-aggregator",
    version="0.1.0",
    description="Annotates variants with population allele frequencies from public datasets.",
    authors=["PGIP Core Team"],
    entrypoint="python -m pgip_plugins.frequency_aggregator",
    created_at=datetime(2025, 10, 4, 0, 0, 0),
    updated_at=datetime(2025, 10, 4, 0, 0, 0),
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


@router.get("/", response_model=list[PluginSummary])
def list_plugins() -> list[PluginSummary]:
    """Return a collection of available plugins."""

    return [
        PluginSummary(
            name=_SAMPLE_MANIFEST.name,
            version=_SAMPLE_MANIFEST.version,
            description=_SAMPLE_MANIFEST.description,
            tags=_SAMPLE_MANIFEST.tags,
            latest_run_at=_SAMPLE_MANIFEST.updated_at,
        )
    ]


@router.get("/{plugin_name}", response_model=PluginManifest)
def get_plugin(plugin_name: str) -> PluginManifest:
    """Return the manifest for a specific plugin."""

    if plugin_name != _SAMPLE_MANIFEST.name:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return _SAMPLE_MANIFEST
