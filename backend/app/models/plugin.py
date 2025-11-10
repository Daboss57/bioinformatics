"""Pydantic models describing plugin manifests and metadata."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class PluginInput(BaseModel):
    """Definition of inputs expected by a plugin."""

    name: str
    description: str
    media_type: Literal[
        "application/vnd.pgip.vcf",
        "application/vnd.pgip.gfa",
        "application/vnd.pgip.graph-selection+json",
        "application/json",
        "text/plain",
    ]
    optional: bool = False


class PluginOutput(BaseModel):
    """Definition of outputs produced by a plugin."""

    name: str
    description: str
    media_type: Literal[
        "application/vnd.pgip.annotation+jsonl",
        "application/json",
        "text/csv",
    ] = "application/vnd.pgip.annotation+jsonl"


class PluginProvenance(BaseModel):
    """Metadata capturing provenance for a plugin build or container image."""

    container_image: str
    container_digest: Optional[str] = None
    repository_url: Optional[HttpUrl] = None
    reference: Optional[str] = None

    @field_validator("container_image")
    @classmethod
    def validate_image(cls, value: str) -> str:
        if ":" not in value and "@" not in value:
            msg = (
                "Container image should include a tag (e.g. image:tag) or digest "
                "(image@sha256:...)."
            )
            raise ValueError(msg)
        return value


class PluginManifest(BaseModel):
    """Top-level manifest describing a PGIP plugin."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    version: str
    description: str
    authors: List[str]
    entrypoint: str
    created_at: datetime
    updated_at: datetime
    inputs: List[PluginInput]
    outputs: List[PluginOutput]
    tags: List[str] = []
    provenance: PluginProvenance
    resources: Optional[dict[str, str]] = None


class PluginSummary(BaseModel):
    """Response model summarizing a plugin for API responses."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    version: str
    description: str
    tags: List[str]
    latest_run_at: Optional[datetime] = None


class PluginTagSummary(BaseModel):
    """Frequency information for a plugin tag."""

    tag: str
    usage_count: int


class PluginStats(BaseModel):
    """Aggregate statistics for the plugin registry."""

    total_plugins: int
    unique_authors: int
    unique_tags: int
    most_recent_update: Optional[datetime] = None
    top_tags: List[PluginTagSummary] = Field(default_factory=list)
