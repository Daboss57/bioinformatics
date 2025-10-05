# PGIP Nextflow Pipelines

This directory houses reproducible workflow definitions used to ingest datasets, execute plugins, and benchmark annotations. The initial placeholder pipeline (`ingest_pangenome.nf`) demonstrates the expected structure.

## Running Locally

```bash
nextflow run ingest_pangenome.nf \
    --vcf data/example.vcf.gz \
    --gfa data/example.gfa \
    --backend_api http://localhost:8000
```

> **Note:** Real tooling, containers, and data validation steps will arrive in subsequent milestones. For now, the pipeline copies input artifacts and prints their locations to the console.

## Design Goals

- Use containerized processes with pinned digests
- Emit provenance metadata consumable by the backend
- Support both human and microbial pangenome ingestion
- Integrate with workflow registries (Dockstore, nf-core) when mature

Contributions that add realistic process blocks, input validation, or integration tests are welcome.
