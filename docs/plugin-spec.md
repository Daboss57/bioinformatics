# PGIP Plugin Specification

This document defines the contract for annotation plugins executed within the PanGenome Insight Platform. Plugins can wrap command-line tools, Python/R scripts, or ML models, as long as they adhere to the manifest and runtime interface described below.

## Guiding Principles

1. **Containerized** – Every plugin is executed from an OCI-compliant container image.
2. **Declarative** – A YAML manifest exposes metadata, inputs, outputs, and resource needs.
3. **Composable** – Plugins can be chained together within workflows using consistent media types.
4. **Auditable** – Provenance (image digest, git revision, authors) is mandatory for reproducibility.
5. **Stateless** – Plugins operate on provided artifacts and emit results to stdout or a designated directory.

## Manifest Schema

Manifests are stored as YAML but validated against the JSON schema outlined below. See `app/models/plugin.py` for the canonical Pydantic definitions.

```yaml
name: string (unique slug)
version: semver string
summary: short description
long_description: optional markdown
entrypoint: command executed inside the container
created_at: ISO 8601 datetime
updated_at: ISO 8601 datetime
authors:
  - name or handle strings
tags:
  - domain keywords
inputs:
  - name: variants
    description: "VCF slice to annotate"
    media_type: application/vnd.pgip.vcf
    optional: false
outputs:
  - name: annotations
    description: "JSONL annotations"
    media_type: application/vnd.pgip.annotation+jsonl
provenance:
  container_image: ghcr.io/pgip/frequency-aggregator:0.1.0
  container_digest: sha256:...
  repository_url: https://github.com/pgip-dev/plugins
  reference: main
resources:
  cpu: "2"
  memory: "4Gi"
  gpu: optional
parameters:
  - name: allele-frequency-threshold
    type: float
    default: 0.01
    description: Minimum frequency to report
compliance:
  - license: MIT
    url: https://opensource.org/license/mit/
```

### Required Fields

| Field | Description |
| --- | --- |
| `name` | Unique slug (lowercase, hyphen-separated) |
| `version` | Follows [SemVer](https://semver.org/) |
| `entrypoint` | Shell command executed in the container |
| `inputs` | At least one input definition |
| `outputs` | At least one output definition |
| `provenance.container_image` | Container reference with tag or digest |

## Runtime Contract

- PGIP mounts the working directory at `/workspace` inside the container.
- Inputs are provided as files inside `/workspace/input/<input-name>/`.
- Plugin must write outputs to `/workspace/output/<output-name>/`.
- Exit code 0 is treated as success; non-zero results surface as failures with logs.
- Plugins can emit structured logs to `/workspace/logs/` (optional).

### Environment Variables

| Variable | Purpose |
| --- | --- |
| `PGIP_RUN_ID` | Unique identifier for the execution instance |
| `PGIP_BACKEND_API` | Base URL for reporting status back to the backend |
| `PGIP_AUTH_TOKEN` | Short-lived token (if auth enabled) |
| `PGIP_PARAMETERS` | JSON blob for runtime parameters |

## CLI Helpers

A future `pgip plugins init` command will scaffold template manifests, entrypoints, and tests. Until then, contributors can copy `templates/plugin-manifest.example.yaml` (to be added).

## Validation & Publication Flow

1. Contributor submits manifest + container image via pull request.
2. CI validates schema, lints YAML, and executes level-0 smoke tests inside GitHub Actions (using a lightweight sample dataset).
3. Upon merge, the manifest is published to the plugin registry table in PostgreSQL and the container digest is frozen.
4. Benchmark workflows periodically evaluate plugins against curated datasets; results appear in the dashboard.

## Media Types

Custom media types follow the prefix `application/vnd.pgip.*`. Initial set:

- `application/vnd.pgip.vcf`
- `application/vnd.pgip.gfa`
- `application/vnd.pgip.graph-selection+json`
- `application/vnd.pgip.annotation+jsonl`

Additional media types can be proposed via issues; document parsing expectations clearly.

## Future Extensions

- Signed manifests (Sigstore) to guarantee integrity
- Plugin dependency graph (run plugin B only after plugin A completes)
- Streaming interface for large graph traversals
- GPU scheduling metadata and benchmarking

Questions? Open a GitHub issue with the `plugin-spec` label.
