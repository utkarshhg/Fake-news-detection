

export default function RiskBadge({ level, color }) {
  return (
    <div
      className="risk-badge"
      style={{
        background: `${color}0f`,
        border: `1px solid ${color}33`,
      }}
    >
      <div className="risk-badge-label">Assessment</div>
      <div className="risk-badge-value" style={{ color }}>{level} Risk</div>
    </div>
  );
}
