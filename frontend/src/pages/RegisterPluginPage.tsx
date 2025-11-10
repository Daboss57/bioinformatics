import { useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { PluginManifest, registerPlugin } from "../api/client";

const buildSampleManifest = (): string =>
  JSON.stringify(
    {
      name: "transcriptomic-overlay",
      version: "1.0.0",
      description: "Overlays gene expression matrices onto variant cohorts.",
      authors: ["PGIP Core Team"],
      entrypoint: "python -m pgip_plugins.transcriptomic_overlay --input /data/variants.vcf",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      inputs: [
        {
          name: "variants",
          description: "VCF dataset to annotate",
          media_type: "application/vnd.pgip.vcf"
        },
        {
          name: "expression",
          description: "Gene expression matrix",
          media_type: "application/json",
          optional: true
        }
      ],
      outputs: [
        {
          name: "annotations",
          description: "Enriched annotations with expression evidence",
          media_type: "application/vnd.pgip.annotation+jsonl"
        }
      ],
      tags: ["expression", "transcriptome"],
      provenance: {
        container_image: "ghcr.io/pgip/transcriptomic-overlay:1.0.0",
        repository_url: "https://github.com/pgip-dev/transcriptomic-overlay"
      },
      resources: {
        cpu: "4",
        memory: "8Gi"
      }
    },
    null,
    2
  );

const RegisterPluginPage = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const sampleManifest = useMemo(() => buildSampleManifest(), []);

  const [manifestText, setManifestText] = useState<string>(sampleManifest);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: async (payload: PluginManifest) => registerPlugin(payload),
    onSuccess: (manifest) => {
      setSuccessMessage(`Registered ${manifest.name} v${manifest.version}`);
      setErrorMessage(null);
      queryClient.invalidateQueries({ queryKey: ["plugins"] });
      queryClient.invalidateQueries({ queryKey: ["plugin-stats"] });
      setTimeout(() => navigate(`/plugins/${manifest.name}`), 1200);
    },
    onError: (error: Error | unknown) => {
      const message = error instanceof Error ? error.message : "Registration failed";
      setErrorMessage(message);
    }
  });

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSuccessMessage(null);

    try {
      const parsed = JSON.parse(manifestText) as PluginManifest;
      mutation.mutate(parsed);
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(`Invalid JSON: ${error.message}`);
      } else {
        setErrorMessage("Invalid JSON payload");
      }
    }
  };

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h2>Register Plugin</h2>
          <p>Paste or tweak a plugin manifest and submit it to the PGIP registry.</p>
        </div>
      </header>

      <form className="plugin-form" onSubmit={handleSubmit}>
        <label htmlFor="manifest">Plugin Manifest (JSON)</label>
        <textarea
          id="manifest"
          name="manifest"
          value={manifestText}
          onChange={(event) => setManifestText(event.target.value)}
          rows={24}
          spellCheck={false}
        />

        <div className="form-actions">
          <button type="button" onClick={() => setManifestText(sampleManifest)}>
            Reset to Sample
          </button>
          <button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? "Submitting…" : "Submit Manifest"}
          </button>
        </div>
      </form>

      {errorMessage ? <p className="error">{errorMessage}</p> : null}
      {successMessage ? <p className="success">{successMessage}</p> : null}
    </section>
  );
};

export default RegisterPluginPage;
