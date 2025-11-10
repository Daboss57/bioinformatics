import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { fetchPluginStats, PluginStats, fetchVcfIngests, VcfIngestRecord } from "../api/client";

const DashboardPage = () => {
  const { data: stats, isLoading, isError } = useQuery<PluginStats, Error>({
    queryKey: ["plugin-stats"],
    queryFn: fetchPluginStats,
    staleTime: 30_000
  });

  const {
    data: ingests,
    isLoading: isLoadingIngests,
    isError: isErrorIngests
  } = useQuery<VcfIngestRecord[], Error>({
    queryKey: ["vcf-ingests"],
    queryFn: () => fetchVcfIngests(5),
    staleTime: 30_000
  });

  return (
    <section className="page dashboard">
      <header className="page-header">
        <div>
          <h2>Welcome to PGIP</h2>
          <p>
            Track your plugin registry, monitor provenance, and launch new annotations from a single place.
          </p>
        </div>
        <Link to="/plugins/new" className="link-button">
          Register Plugin
        </Link>
      </header>

      <div className="stat-grid">
        <article className="stat-card">
          <span className="stat-value">{isLoading ? "…" : stats?.total_plugins ?? 0}</span>
          <span className="stat-label">Total Plugins</span>
        </article>
        <article className="stat-card">
          <span className="stat-value">{isLoading ? "…" : stats?.unique_authors ?? 0}</span>
          <span className="stat-label">Contributing Authors</span>
        </article>
        <article className="stat-card">
          <span className="stat-value">{isLoading ? "…" : stats?.unique_tags ?? 0}</span>
          <span className="stat-label">Unique Tags</span>
        </article>
        <article className="stat-card">
          <span className="stat-value">
            {isLoading
              ? "…"
              : stats?.most_recent_update
              ? new Date(stats.most_recent_update).toLocaleString()
              : "—"}
          </span>
          <span className="stat-label">Most Recent Update</span>
        </article>
      </div>

      <div className="card-grid">
        <article className="card">
          <h3>Top Tags</h3>
          {isError ? (
            <p className="error">Failed to load stats.</p>
          ) : stats?.top_tags?.length ? (
            <ul className="tag-cloud">
              {stats.top_tags.map((tag) => (
                <li key={tag.tag}>
                  <span>{tag.tag}</span>
                  <small>{tag.usage_count} uses</small>
                </li>
              ))}
            </ul>
          ) : (
            <p>No tag usage yet. Register your first plugin to populate insights.</p>
          )}
        </article>

        <article className="card">
          <h3>Next Actions</h3>
          <ul className="bullet-list">
            <li>Register a new plugin via the form or CLI.</li>
            <li>Kick off an annotation workflow through Nextflow.</li>
            <li>Wire live provenance events into this dashboard.</li>
          </ul>
        </article>

        <article className="card">
          <h3>Recent Ingests</h3>
          {isErrorIngests ? (
            <p className="error">Failed to load ingest history.</p>
          ) : isLoadingIngests ? (
            <p>Loading…</p>
          ) : ingests && ingests.length ? (
            <table className="ingest-list">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Source</th>
                  <th>Records</th>
                  <th>Samples</th>
                  <th>Ingested</th>
                </tr>
              </thead>
              <tbody>
                {ingests.map((record) => (
                  <tr key={record.id}>
                    <td>{record.id}</td>
                    <td title={record.source}>{record.source}</td>
                    <td>{record.records}</td>
                    <td>{record.samples?.length ? record.samples.join(", ") : "–"}</td>
                    <td>{new Date(record.ingested_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No ingest runs recorded yet. Use the CLI to execute the sample workflow.</p>
          )}
        </article>
      </div>
    </section>
  );
};

export default DashboardPage;
