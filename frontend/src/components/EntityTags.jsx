

const COLOR_MAP = {
  PERSON: '#3538cd',
  ORG: '#067647',
  GPE: '#b54708',
  LOC: '#b54708',
  DATE: '#6938ef',
  EVENT: '#b42318',
  MONEY: '#0e7090',
  NORP: '#1570ef',
};

export default function EntityTags({ entities = [] }) {
  if (!entities.length) return <p className="text-muted text-sm">No entities extracted.</p>;

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
      {entities.slice(0, 20).map((ent, i) => {
        const color = COLOR_MAP[ent.label] || '#475467';
        return (
          <span
            key={i}
            className="tag"
            style={{
              background: `${color}0f`,
              color,
              border: `1px solid ${color}2e`,
            }}
          >
            {ent.text}
            <span style={{ opacity: 0.65, fontSize: '0.68rem', fontWeight: 500 }}>
              {ent.description || ent.label}
            </span>
          </span>
        );
      })}
    </div>
  );
}
