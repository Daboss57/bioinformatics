"""PGIP Typer application."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import httpx
import typer
from pydantic import BaseModel, ValidationError
from rich.console import Console
from rich.table import Table

DEFAULT_API_URL = "http://localhost:8000"
console = Console()


class PluginSummary(BaseModel):
    name: str
    version: str
    description: str
    tags: list[str] = []
    latest_run_at: Optional[str] = None


class PluginManifest(BaseModel):
    name: str
    version: str
    description: str
    authors: list[str]
    entrypoint: str
    created_at: str
    updated_at: str
    inputs: list[dict]
    outputs: list[dict]
    tags: list[str] = []
    provenance: dict
    resources: Optional[dict] = None


class PluginTagSummary(BaseModel):
    tag: str
    usage_count: int


class PluginStats(BaseModel):
    total_plugins: int
    unique_authors: int
    unique_tags: int
    most_recent_update: Optional[str] = None
    top_tags: list[PluginTagSummary] = []


class AssetIngestRecord(BaseModel):
    """Representation of a dataset ingest summary."""

    id: int
    source: str
    records: int
    samples: list[str] = []
    gfa_stats: dict[str, Any] | None = None
    created_at: datetime
    ingested_at: datetime


def _client(base_url: str) -> httpx.Client:
    return httpx.Client(base_url=base_url, timeout=10.0)


def _get_base_url(api_url: Optional[str]) -> str:
    return api_url or os.getenv("PGIP_BACKEND_URL", DEFAULT_API_URL)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_nextflow(explicit_path: Optional[Path]) -> str:
    if explicit_path is not None:
        if not explicit_path.exists():
            console.print(f"[red]Error:[/] Nextflow executable not found at {explicit_path}")
            raise typer.Exit(1)
        return str(explicit_path)

    discovered = shutil.which("nextflow")
    if discovered:
        return discovered

    console.print(
        "[red]Nextflow executable not found.[/] Install Nextflow and ensure it is on your PATH, "
        "or pass --nextflow-bin to the command."
    )
    raise typer.Exit(1)


app = typer.Typer(help="Interact with the PanGenome Insight Platform backend.")
plugins_app = typer.Typer(help="Manage annotation plugins.")
pipelines_app = typer.Typer(help="Execute sample pipelines.")
app.add_typer(plugins_app, name="plugins")
app.add_typer(pipelines_app, name="pipelines")


@plugins_app.command("list")
def list_plugins(api_url: Optional[str] = typer.Option(None, help="Override backend API URL")) -> None:
    """List available plugins."""

    base_url = _get_base_url(api_url)
    with _client(base_url) as client:
        response = client.get("/api/v1/plugins/")
    if response.status_code != 200:
        console.print(f"[red]Error:[/] {response.text}")
        raise typer.Exit(code=1)

    try:
        payload = [PluginSummary.model_validate(item) for item in response.json()]
    except ValidationError as exc:
        console.print(f"[red]Failed to parse response:[/] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title="PGIP Plugins")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Version", style="magenta")
    table.add_column("Description")
    table.add_column("Tags", style="green")

    for plugin in payload:
        tags = ", ".join(plugin.tags) if plugin.tags else "-"
        table.add_row(plugin.name, plugin.version, plugin.description, tags)

    console.print(table)


@plugins_app.command("stats")
def plugin_stats(api_url: Optional[str] = typer.Option(None, help="Override backend API URL")) -> None:
    """Display aggregate registry statistics."""

    base_url = _get_base_url(api_url)
    with _client(base_url) as client:
        response = client.get("/api/v1/plugins/stats")

    if response.status_code != 200:
        console.print(f"[red]Error:[/] {response.text}")
        raise typer.Exit(code=1)

    try:
        stats = PluginStats.model_validate(response.json())
    except ValidationError as exc:
        console.print(f"[red]Failed to parse stats:[/] {exc}")
        raise typer.Exit(code=1) from exc

    console.print("[bold]Plugin Registry Stats[/bold]")
    console.print(f"Total plugins: [cyan]{stats.total_plugins}[/cyan]")
    console.print(f"Unique authors: [cyan]{stats.unique_authors}[/cyan]")
    console.print(f"Unique tags: [cyan]{stats.unique_tags}[/cyan]")
    if stats.most_recent_update:
        console.print(f"Last update: [cyan]{stats.most_recent_update}[/cyan]")

    if stats.top_tags:
        tag_table = Table(show_header=True, header_style="bold blue")
        tag_table.add_column("Tag")
        tag_table.add_column("Usage")
        for tag in stats.top_tags:
            tag_table.add_row(tag.tag, str(tag.usage_count))
        console.print(tag_table)
    else:
        console.print("No tag usage data yet.")


@plugins_app.command("show")
def show_plugin(
    name: str = typer.Argument(..., help="Plugin name"),
    version: Optional[str] = typer.Option(None, help="Optional plugin version"),
    api_url: Optional[str] = typer.Option(None, help="Override backend API URL"),
    output: Optional[Path] = typer.Option(None, help="Write manifest JSON to file"),
) -> None:
    """Show manifest details for a plugin."""

    base_url = _get_base_url(api_url)
    params = {"version": version} if version else None

    with _client(base_url) as client:
        response = client.get(f"/api/v1/plugins/{name}", params=params)

    if response.status_code != 200:
        console.print(f"[red]Error:[/] {response.text}")
        raise typer.Exit(code=1)

    try:
        manifest = PluginManifest.model_validate(response.json())
    except ValidationError as exc:
        console.print(f"[red]Failed to parse manifest:[/] {exc}")
        raise typer.Exit(code=1) from exc

    if output:
        output.write_text(json.dumps(manifest.model_dump(mode="json"), indent=2))
        console.print(f"Manifest written to {output}")
        return

    console.print_json(data=manifest.model_dump(mode="json"))


@plugins_app.command("register")
def register_plugin(
    manifest_path: Path = typer.Argument(..., exists=True, readable=True, help="Path to manifest JSON"),
    api_url: Optional[str] = typer.Option(None, help="Override backend API URL"),
) -> None:
    """Register or update a plugin manifest from a JSON file."""

    base_url = _get_base_url(api_url)

    try:
        manifest_data = json.loads(manifest_path.read_text())
        manifest = PluginManifest.model_validate(manifest_data)
    except (json.JSONDecodeError, ValidationError) as exc:
        console.print(f"[red]Invalid manifest:[/] {exc}")
        raise typer.Exit(code=1) from exc

    with _client(base_url) as client:
        response = client.post("/api/v1/plugins/", json=manifest.model_dump(mode="json"))

    if response.status_code not in (200, 201):
        console.print(f"[red]Error:[/] {response.text}")
        raise typer.Exit(code=1)

    console.print(f"[green]Registered plugin {manifest.name} v{manifest.version}[/]")


@pipelines_app.command("run")
def run_pipeline(
    vcf: Optional[Path] = typer.Option(
        None,
        "--vcf",
        help="Path to a VCF dataset",
    ),
    gfa: Optional[Path] = typer.Option(
        None,
        "--gfa",
        help="Path to a GFA graph file",
    ),
    backend_api: Optional[str] = typer.Option(
        None,
        "--backend-api",
        help="Override backend API URL",
    ),
    publish_dir: Optional[Path] = typer.Option(
        None,
        "--publish-dir",
        help="Directory to publish pipeline outputs",
    ),
    nextflow_bin: Optional[Path] = typer.Option(
        None,
        "--nextflow-bin",
        help="Path to the Nextflow executable if not on PATH",
    ),
    resume: bool = typer.Option(
        False,
        "--resume/--no-resume",
        help="Resume a previous Nextflow run",
    ),
) -> None:
    """Execute the sample ingest pipeline using the bundled assets."""

    repo_root = _repo_root()
    pipeline_path = repo_root / "workflows" / "nextflow" / "ingest_pangenome.nf"
    if not pipeline_path.exists():
        console.print(f"[red]Error:[/] Pipeline definition not found at {pipeline_path}")
        raise typer.Exit(1)

    vcf_path = (vcf or repo_root / "data" / "variants" / "example.vcf").resolve()
    gfa_path = (gfa or repo_root / "data" / "graphs" / "example.gfa").resolve()
    publish_path = (publish_dir or repo_root / "results" / "ingest").resolve()
    publish_path.mkdir(parents=True, exist_ok=True)

    for label, path in ("VCF", vcf_path), ("GFA", gfa_path):
        if not path.exists():
            console.print(f"[red]Error:[/] {label} file not found at {path}")
            raise typer.Exit(1)

    api_url = _get_base_url(backend_api)
    nextflow_exec = _resolve_nextflow(nextflow_bin)

    cmd = [nextflow_exec, "run", str(pipeline_path)]
    if resume:
        cmd.append("-resume")
    cmd.extend(
        [
            "--vcf",
            str(vcf_path),
            "--gfa",
            str(gfa_path),
            "--publish_dir",
            str(publish_path),
            "--backend_api",
            api_url,
        ]
    )

    console.print("[cyan]Running Nextflow pipeline:[/] " + " ".join(cmd))

    process = subprocess.Popen(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    assert process.stdout is not None  # for type checkers
    try:
        for line in process.stdout:
            console.print(line.rstrip())
    except KeyboardInterrupt:  # pragma: no cover - user interruption
        process.terminate()
        raise
    return_code = process.wait()

    if return_code != 0:
        console.print(f"[red]Pipeline failed with exit code {return_code}[/]")
        raise typer.Exit(return_code)

    console.print(f"[green]Pipeline completed successfully. Outputs in {publish_path}[/]")


@pipelines_app.command("list")
def list_ingests(
    limit: int = typer.Option(10, min=1, max=100, help="Number of ingest records to display"),
    api_url: Optional[str] = typer.Option(None, help="Override backend API URL"),
) -> None:
    """Display recent ingest summaries captured by the backend."""

    base_url = _get_base_url(api_url)
    with _client(base_url) as client:
        response = client.get("/api/v1/assets/vcf", params={"limit": limit})

    if response.status_code != 200:
        console.print(f"[red]Error:[/] {response.text}")
        raise typer.Exit(code=1)

    try:
        payload = [AssetIngestRecord.model_validate(item) for item in response.json()]
    except ValidationError as exc:
        console.print(f"[red]Failed to parse ingest records:[/] {exc}")
        raise typer.Exit(code=1) from exc

    if not payload:
        console.print("No ingest history yet. Run `pgip pipelines run` to record your first dataset.")
        return

    table = Table(title="Recent VCF Ingests")
    table.add_column("ID", justify="right")
    table.add_column("Source")
    table.add_column("Records", justify="right")
    table.add_column("Samples")
    table.add_column("Ingested")

    for record in payload:
        table.add_row(
            str(record.id),
            record.source,
            str(record.records),
            ", ".join(record.samples) if record.samples else "–",
            record.ingested_at.astimezone().strftime("%Y-%m-%d %H:%M"),
        )

    console.print(table)


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    app()
