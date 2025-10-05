#!/usr/bin/env nextflow

/*
 * PGIP Nextflow pipeline: Ingest pangenome assets.
 *
 * This placeholder pipeline demonstrates how VCF and GFA assets could be
 * normalized and registered with the backend API. Future iterations will add
 * container images, real tools, and provenance reporting.
 */

nextflow.enable.dsl=2

params.vcf = params.vcf ?: "data/example.vcf.gz"
params.gfa = params.gfa ?: "data/example.gfa"
params.backend_api = params.backend_api ?: "http://localhost:8000"

process PREPARE_VCF {
    tag "vcf:${params.vcf}"

    input:
    path vcf_file

    output:
    path "prepared.vcf.gz"

    script:
    """
    cp ${vcf_file} prepared.vcf.gz
    """
}

process PREPARE_GFA {
    tag "gfa:${params.gfa}"

    input:
    path gfa_file

    output:
    path "prepared.gfa"

    script:
    """
    cp ${gfa_file} prepared.gfa
    """
}

workflow {
    Channel.fromPath(params.vcf).set { vcf_channel }
    Channel.fromPath(params.gfa).set { gfa_channel }

    PREPARE_VCF(vcf_channel)
    PREPARE_GFA(gfa_channel)

    prepared_vcf = PREPARE_VCF.out
    prepared_gfa = PREPARE_GFA.out

    prepared_vcf.view { "Prepared VCF: ${it}" }
    prepared_gfa.view { "Prepared GFA: ${it}" }

    // TODO: Invoke backend API to register assets once the ingestion endpoint exists.
}
