export default function Meter({ value, tone = '', label }) {
  const v = Math.max(0, Math.min(100, value));
  return <div className={`meter ${tone}`} role="progressbar" aria-valuenow={v} aria-valuemin={0} aria-valuemax={100} aria-label={label}><i style={{ width: `${v}%` }} /></div>;
}
