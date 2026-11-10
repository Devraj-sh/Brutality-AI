import { Link } from 'react-router-dom';

/** The vibrant golden Brutality AI warrior emblem mark */
export function LogoMark({ size = 36, className = '' }) {
  return (
    <img
      src="/logo-mark.png"
      alt="Brutality AI Emblem"
      width={size}
      height={size}
      className={`logo-mark-img ${className}`}
      style={{ display: 'inline-block', verticalAlign: 'middle', objectFit: 'contain' }}
    />
  );
}

/** Full Brutality AI logo in vibrant golden yellow */
export default function Logo({ to = '/', dark = false, variant = 'gold', height = 36 }) {
  const src = dark ? '/logo-dark.png' : variant === 'nav' ? '/logo-nav.png' : '/logo-gold.png';
  return (
    <Link to={to} className={`logo ${dark ? 'dark' : ''}`} aria-label="Brutality AI home">
      <img
        src={src}
        alt="Brutality AI"
        height={height}
        className="logo-img"
        style={{ height: `${height}px`, width: 'auto', display: 'block', objectFit: 'contain' }}
      />
    </Link>
  );
}
