

function scoreColor(score) {
  if (score >= 75) return 'var(--success)';
  if (score >= 50) return 'var(--warning)';
  if (score >= 25) return '#c4320a';
  return 'var(--danger)';
}

export default function BreakdownTable({ breakdown = {} }) {
  return Object.entries(breakdown).map(([key, data]) => {
    const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    const score = data.score || 0;
    const weight = (data.weight || 0) * 100;
    const weighted = data.weighted_score || 0;
    const color = scoreColor(score);

    return (
      <div className="breakdown-row" key={key}>
        <div className="breakdown-label">{label}</div>
        <div className="breakdown-track">
          <div className="breakdown-fill" style={{ width: `${score}%`, background: color }} />
        </div>
        <div className="breakdown-score" style={{ color }}>{score.toFixed(0)}</div>
      </div>
    );
  });
}
