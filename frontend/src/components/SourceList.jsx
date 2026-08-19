

export default function SourceList({ sources = [] }) {
  if (!sources.length) return <div className="alert alert-info">No matching sources found.</div>;

  return sources.map((src, i) => {
    const trusted = src.is_trusted;
    const color = trusted ? 'var(--success)' : 'var(--ink-muted)';
    return (
      <div className="source-card" key={i}>
        <div className="source-card-header">
          <span className="source-card-title">{(src.title || '').slice(0, 80)}</span>
          <span
            className="source-card-badge"
            style={{
              background: `${trusted ? '#067647' : '#8a94a6'}12`,
              color,
              border: `1px solid ${trusted ? '#067647' : '#8a94a6'}30`,
            }}
          >
            {trusted ? 'Trusted' : 'Source'}
          </span>
        </div>
        <div className="source-card-meta">
          {src.source} &middot;{' '}
          <a href={src.url} target="_blank" rel="noreferrer" style={{ fontWeight: 600 }}>
            Read article &rarr;
          </a>
        </div>
      </div>
    );
  });
}
