export default function Card({ tone = '', hover = true, as: Tag = 'div', className = '', children, ...rest }) {
  return <Tag className={`tactile-card ${tone} ${hover ? 'hoverable' : ''} ${className}`} {...rest}>{children}</Tag>;
}
export function StatCard({ label, value, suffix = '', icon: Icon, tone = '', hint }) {
  return (
    <Card tone={tone} className="stat-card">
      <div className="stat-top"><span className="stat-label">{label}</span>{Icon && <Icon size={18} />}</div>
      <div className="stat-value num3d">{value}<small>{suffix}</small></div>
      {hint && <div className="stat-hint">{hint}</div>}
    </Card>
  );
}
