import { Link } from 'react-router-dom';
export function LogoMark({ size = 34 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 34 34" aria-hidden="true">
      <rect x="1" y="3.5" width="32" height="30" rx="9" fill="#000000" />
      <rect x="1" y="0.5" width="32" height="30" rx="9" fill="#D6FF3D" stroke="#8fad00" strokeWidth="1.5" />
      <path d="M10.5 7.5h8.2a4.6 4.6 0 0 1 2.1 8.7 5.2 5.2 0 0 1-1.7 10.3h-8.6z" fill="#111318" />
      <path d="M14.4 11.4v3.6h3.5a1.8 1.8 0 0 0 0-3.6zm0 7.6v3.6h4.1a1.8 1.8 0 0 0 0-3.6z" fill="#D6FF3D" />
    </svg>
  );
}
export default function Logo({ to = '/', dark = false }) {
  return (
    <Link to={to} className={`logo ${dark ? 'dark' : ''}`} aria-label="Brutality AI home">
      <LogoMark />
      <span>BRUTALITY<span className="logo-ai">AI</span></span>
    </Link>
  );
}
