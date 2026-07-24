

export default function MetricCard({ label, value, delta }) {
  const deltaColor = delta && delta.includes('+') ? 'var(--success)' : 'var(--danger)';

  return (
    <div className="metric-card">
      <div className="metric-card-label">{label}</div>
      <div className="metric-card-value">{value}</div>
      {delta && (
        <div style={{ marginTop: 6, fontSize: '0.76rem', fontWeight: 600, color: deltaColor }}>
          {delta}
        </div>
      )}
    </div>
  );
}
