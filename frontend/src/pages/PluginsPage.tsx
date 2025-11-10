import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { fetchPlugins, PluginSummary } from "../api/client";

const PluginsPage = () => {
  const { data, isLoading, isError, error } = useQuery<PluginSummary[], Error>({
    queryKey: ["plugins"],
    queryFn: fetchPlugins,
    staleTime: 30_000
  });

  const [searchTerm, setSearchTerm] = useState("");
  const [activeTag, setActiveTag] = useState<string | null>(null);

  const tagOptions = useMemo(() => {
    const tags = new Set<string>();
    data?.forEach((plugin) => plugin.tags?.forEach((tag) => tags.add(tag)));
    return Array.from(tags).sort((a, b) => a.localeCompare(b));
  }, [data]);

  const filteredPlugins = useMemo(() => {
    if (!data) {
      return [] as PluginSummary[];
    }

    return data.filter((plugin) => {
      const matchesTag = activeTag ? plugin.tags?.includes(activeTag) : true;
      if (!matchesTag) return false;

      if (!searchTerm) return true;
      const haystack = `${plugin.name} ${plugin.description}`.toLowerCase();
      return haystack.includes(searchTerm.toLowerCase());
    });
  }, [data, activeTag, searchTerm]);

  if (isLoading) {
    return (
      <section className="page">
        <p>Loading plugins…</p>
      </section>
    );
  }

  if (isError) {
    return (
      <section className="page">
        <p className="error">Failed to load plugins: {error.message}</p>
      </section>
    );
  }

  return (
    <section className="page">
      <header className="page-header">
        <h2>Plugin Registry</h2>
        <p>Browse, filter, and drill into registered annotation modules sourced directly from the backend API.</p>
      </header>

      <div className="filters">
        <input
          type="search"
          placeholder="Search by name or description"
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
        />

        <div className="tag-filter">
          <button
            type="button"
            className={!activeTag ? "tag-chip active" : "tag-chip"}
            onClick={() => setActiveTag(null)}
          >
            All tags
          </button>
          {tagOptions.map((tag) => (
            <button
              type="button"
              key={tag}
              className={activeTag === tag ? "tag-chip active" : "tag-chip"}
              onClick={() => setActiveTag(tag)}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      <div className="card-grid">
        {filteredPlugins.map((plugin: PluginSummary) => (
          <article key={`${plugin.name}-${plugin.version}`} className="card">
            <header>
              <h3>{plugin.name}</h3>
              <span className="version">v{plugin.version}</span>
            </header>
            <p>{plugin.description}</p>
            {plugin.tags?.length ? (
              <ul className="tag-list">
                {plugin.tags.map((tag) => (
                  <li key={tag}>{tag}</li>
                ))}
              </ul>
            ) : null}
            <footer>
              <Link to={`/plugins/${plugin.name}`} className="link-button">
                View Details
              </Link>
            </footer>
          </article>
        ))}
        {!filteredPlugins.length && (data?.length ?? 0) > 0 && (
          <article className="card">
            <h3>No matches</h3>
            <p>Adjust the tag filter or search query to discover other plugins.</p>
          </article>
        )}
        {!data?.length && (
          <article className="card">
            <h3>No plugins yet</h3>
            <p>
              Register a plugin using the backend API or CLI. Once added it will appear here with
              provenance metadata.
            </p>
          </article>
        )}
      </div>
    </section>
  );
};

export default PluginsPage;
