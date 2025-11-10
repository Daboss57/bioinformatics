import { useMemo } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { fetchPlugin, PluginManifest } from "../api/client";

const PluginDetailPage = () => {
  const { name = "" } = useParams();

  const {
    data: manifest,
    isLoading,
    isError,
    error
  } = useQuery<PluginManifest, Error>({
    queryKey: ["plugin", name],
    queryFn: () => fetchPlugin(name),
    enabled: Boolean(name)
  });

  const sortedTags = useMemo(() => manifest?.tags?.slice().sort() ?? [], [manifest?.tags]);

  if (!name) {
    return (
      <section className="page">
        <p className="error">Plugin name missing from URL.</p>
      </section>
    );
  }

  if (isLoading) {
    return (
      <section className="page">
        <p>Loading plugin details…</p>
      </section>
    );
  }

  if (isError) {
    return (
      <section className="page">
        <p className="error">Failed to load plugin: {error.message}</p>
        <Link to="/plugins" className="link-button">
          Back to plugins
        </Link>
      </section>
    );
  }

  if (!manifest) {
    return (
      <section className="page">
        <p>No manifest found.</p>
        <Link to="/plugins" className="link-button">
          Back to plugins
        </Link>
      </section>
    );
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h2>{manifest.name}</h2>
          <span className="version">v{manifest.version}</span>
        </div>
        <Link to="/plugins" className="link-button">
          Back to registry
        </Link>
      </header>

      <article className="detail-card">
        <p>{manifest.description}</p>
        <div className="meta-row">
          <span>
            Created: <strong>{new Date(manifest.created_at).toLocaleString()}</strong>
          </span>
          <span>
            Updated: <strong>{new Date(manifest.updated_at).toLocaleString()}</strong>
          </span>
        </div>
        {sortedTags.length ? (
          <ul className="tag-list">
            {sortedTags.map((tag) => (
              <li key={tag}>{tag}</li>
            ))}
          </ul>
        ) : null}

        <section>
          <h3>Entrypoint</h3>
          <code>{manifest.entrypoint}</code>
        </section>

        <section>
          <h3>Authors</h3>
          <ul>
            {manifest.authors.map((author) => (
              <li key={author}>{author}</li>
            ))}
          </ul>
        </section>

        <section className="grid">
          <div>
            <h3>Inputs</h3>
            <ul>
              {manifest.inputs.map((input) => (
                <li key={input.name}>
                  <strong>{input.name}</strong> ({input.media_type})
                  <p>{input.description}</p>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3>Outputs</h3>
            <ul>
              {manifest.outputs.map((output) => (
                <li key={output.name}>
                  <strong>{output.name}</strong> ({output.media_type})
                  <p>{output.description}</p>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section>
          <h3>Provenance</h3>
          <dl className="definition-list">
            <div>
              <dt>Container Image</dt>
              <dd>{manifest.provenance.container_image}</dd>
            </div>
            {manifest.provenance.container_digest ? (
              <div>
                <dt>Digest</dt>
                <dd>{manifest.provenance.container_digest}</dd>
              </div>
            ) : null}
            {manifest.provenance.repository_url ? (
              <div>
                <dt>Repository</dt>
                <dd>
                  <a href={manifest.provenance.repository_url} target="_blank" rel="noreferrer">
                    {manifest.provenance.repository_url}
                  </a>
                </dd>
              </div>
            ) : null}
            {manifest.provenance.reference ? (
              <div>
                <dt>Reference</dt>
                <dd>{manifest.provenance.reference}</dd>
              </div>
            ) : null}
          </dl>
        </section>
      </article>
    </section>
  );
};

export default PluginDetailPage;
