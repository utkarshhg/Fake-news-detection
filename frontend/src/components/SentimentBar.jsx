

export default function SentimentBar({ polarity = 0, subjectivity = 0 }) {
  const polarityNorm = ((polarity + 1) / 2) * 100;
  const pColor = polarity > 0.1 ? 'var(--success)' : polarity < -0.1 ? 'var(--danger)' : 'var(--warning)';
  const subLabel = subjectivity < 0.4 ? 'Objective' : subjectivity < 0.7 ? 'Subjective' : 'Very Subjective';

  return (
    <div className="grid grid-2" style={{ gap: 24 }}>
      <div>
        <div className="text-muted text-sm mb-sm">Polarity</div>
        <div className="progress-bar">
          <div className="progress-bar-fill" style={{ width: `${polarityNorm}%`, background: pColor }} />
        </div>
        <div className="text-center font-bold mt-sm font-display" style={{ color: pColor }}>
          {polarity >= 0 ? '+' : ''}{polarity.toFixed(2)}
        </div>
      </div>
      <div>
        <div className="text-muted text-sm mb-sm">Subjectivity</div>
        <div className="progress-bar">
          <div className="progress-bar-fill" style={{ width: `${subjectivity * 100}%` }} />
        </div>
        <div className="text-center font-bold mt-sm font-display text-soft">
          {subjectivity.toFixed(2)} ({subLabel})
        </div>
      </div>
    </div>
  );
}
