# PGIP Backend

This directory contains the FastAPI service responsible for orchestrating workflows, managing plugin metadata, and exposing annotation results.

## Features (MVP)

- `/health` heartbeat endpoint for service monitoring
- `/api/v1/plugins/` listing endpoint returning sample manifest data
- CORS configuration for future frontend integration
- Pydantic-based settings management via environment variables

## Local Development

```powershell
# Create a virtual environment (optional but recommended)
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

# Run tests
pytest

# Start the dev server
uvicorn app.main:app --reload
```

Environment variables can be defined in a `.env` file at the project root. The following settings are currently supported:

- `PGIP_API_V1_PREFIX`
- `PGIP_PROJECT_NAME`
- `PGIP_DESCRIPTION`
- `PGIP_ALLOWED_ORIGINS`
- `PGIP_DOCS_URL`
- `PGIP_OPENAPI_URL`

## Next Steps

- Replace the in-memory plugin manifest with persistence (PostgreSQL)
- Add gRPC or message bus integration for workflow orchestration
- Introduce authentication/authorization once multi-user mode begins
