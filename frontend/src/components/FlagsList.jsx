

export default function FlagsList({ flags = [] }) {
  if (!flags.length) return <div className="alert alert-success">No warning flags detected.</div>;

  return flags.map((flag, i) => (
    <div className="flag-item" key={i}>{flag}</div>
  ));
}
