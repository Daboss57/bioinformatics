#!/usr/bin/env nextflow

/*
 * PGIP Nextflow pipeline: Ingest pangenome assets.
 *
 * This placeholder pipeline demonstrates how VCF and GFA assets could be
 * normalized and registered with the backend API. Future iterations will add
 * container images, real tools, and provenance reporting.
 */

nextflow.enable.dsl=2

params.vcf = params.vcf ?: "data/variants/example.vcf"
params.gfa = params.gfa ?: "data/graphs/example.gfa"
params.backend_api = params.backend_api ?: "http://127.0.0.1:8000"
params.publish_dir = params.publish_dir ?: "results/ingest"

process PREPARE_VCF {
    tag "vcf:${params.vcf}"
    publishDir params.publish_dir, mode: "copy", overwrite: true, pattern: "normalized.*"

    input:
    path vcf_file

    output:
    tuple path("normalized.vcf"), path("normalized.vcf.summary.json")

    script:
    """
    python - <<'PY'
    import json
    import pathlib
    import shutil
    from datetime import datetime, timezone

    vcf_path = pathlib.Path("${vcf_file}")
    shutil.copy(vcf_path, pathlib.Path("normalized.vcf"))

    total_records = 0
    samples = []


    with vcf_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("##"):
                continue
            if line.startswith("#CHROM"):
                header_columns = line.rstrip().split("\t")
                samples = header_columns[9:]
                continue
            if line.strip():
                total_records += 1

    summary = {
        "source": str(vcf_path),
        "records": total_records,
        "samples": samples,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    pathlib.Path("normalized.vcf.summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    PY
    """
}

process SUMMARIZE_GFA {
    tag "gfa:${params.gfa}"
    publishDir params.publish_dir, mode: "copy", overwrite: true, pattern: "gfa.*"

    input:
    path gfa_file

    output:
    path "gfa.stats.json"

    script:
    """
    python - <<'PY'
    import json
    import pathlib
    from datetime import datetime, timezone

    gfa_path = pathlib.Path("${gfa_file}")

    segments = 0
    links = 0
    sequence_bases = 0

    with gfa_path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            record_type = line[0]
            if record_type == "S":
                segments += 1
                parts = line.split("\t")
                if len(parts) > 2 and parts[2] not in {"*", ""}:
                    sequence_bases += len(parts[2])
            elif record_type in {"L", "E"}:
                links += 1

    stats = {
        "source": str(gfa_path),
        "segments": segments,
        "links": links,
        "sequence_bases": sequence_bases,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    pathlib.Path("gfa.stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    PY
    """
}

process REGISTER_ASSETS {
    tag "register"
    publishDir params.publish_dir, mode: "copy", overwrite: true, pattern: "registration-response.json"

    input:
    tuple path(summary_json), path(gfa_stats)

    output:
    path "registration-response.json"

    script:
    """
    python - <<'PY'
    import json
    import pathlib
    import urllib.error
    import urllib.request

    api = "${params.backend_api}".rstrip("/")
    summary_path = pathlib.Path("${summary_json}")
    gfa_path = pathlib.Path("${gfa_stats}")

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    payload["gfa_stats"] = json.loads(gfa_path.read_text(encoding="utf-8"))

    request = urllib.request.Request(
        url=f"{api}/api/v1/assets/vcf",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        content = json.dumps({"error": str(exc)})

    pathlib.Path("registration-response.json").write_text(content, encoding="utf-8")
    PY
    """
}

workflow {
    Channel.fromPath(params.vcf).set { vcf_channel }
    Channel.fromPath(params.gfa).set { gfa_channel }

    summaries = PREPARE_VCF(vcf_channel)
    gfa_stats = SUMMARIZE_GFA(gfa_channel)

    REGISTER_ASSETS(summaries.combine(gfa_stats))
}
