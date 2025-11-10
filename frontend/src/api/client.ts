import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  timeout: 8000
});

export interface PluginSummary {
  name: string;
  version: string;
  description: string;
  tags: string[];
  latest_run_at?: string | null;
}

export interface PluginManifest {
  name: string;
  version: string;
  description: string;
  authors: string[];
  entrypoint: string;
  created_at: string;
  updated_at: string;
  inputs: Array<{
    name: string;
    description: string;
    media_type: string;
    optional?: boolean;
  }>;
  outputs: Array<{
    name: string;
    description: string;
    media_type: string;
  }>;
  tags: string[];
  provenance: {
    container_image: string;
    container_digest?: string | null;
    repository_url?: string | null;
    reference?: string | null;
  };
  resources?: Record<string, string> | null;
}

export interface PluginTagSummary {
  tag: string;
  usage_count: number;
}

export interface PluginStats {
  total_plugins: number;
  unique_authors: number;
  unique_tags: number;
  most_recent_update?: string | null;
  top_tags: PluginTagSummary[];
}

export interface VcfIngestRecord {
  id: number;
  source: string;
  records: number;
  samples: string[];
  gfa_stats?: Record<string, unknown> | null;
  created_at: string;
  ingested_at: string;
}

export const fetchPlugins = async (): Promise<PluginSummary[]> => {
  const response = await api.get<PluginSummary[]>("/api/v1/plugins/");
  return response.data;
};

export const fetchPlugin = async (name: string): Promise<PluginManifest> => {
  const response = await api.get<PluginManifest>(`/api/v1/plugins/${name}`);
  return response.data;
};

export const fetchPluginStats = async (): Promise<PluginStats> => {
  const response = await api.get<PluginStats>("/api/v1/plugins/stats");
  return response.data;
};

export const fetchVcfIngests = async (limit = 5): Promise<VcfIngestRecord[]> => {
  const response = await api.get<VcfIngestRecord[]>("/api/v1/assets/vcf", {
    params: { limit }
  });
  return response.data;
};

export const registerPlugin = async (manifest: PluginManifest): Promise<PluginManifest> => {
  const response = await api.post<PluginManifest>("/api/v1/plugins/", manifest);
  return response.data;
};

export default api;
