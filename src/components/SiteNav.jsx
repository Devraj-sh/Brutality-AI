import { useEffect, useState } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, ArrowUpRight } from 'lucide-react';
import Logo from './Logo.jsx';
import Button from './Button.jsx';

const LINKS = [
  { label: 'Home', to: '/', id: 'top' },
  { label: 'How It Works', to: '/#how', id: 'how' },
  { label: 'Accountability Theory', to: '/#theory', id: 'theory' },
  { label: 'AI Agents', to: '/#agents', id: 'agents' },
  { label: 'Reality Reports', to: '/#report', id: 'report' },
  { label: 'Pricing', to: '/#pricing', id: 'pricing' },
];

export default function SiteNav() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive] = useState('top');
  const { pathname } = useLocation();
  const navigate = useNavigate();

  useEffect(() => { const f = () => setScrolled(window.scrollY > 10); f(); addEventListener('scroll', f, { passive: true }); return () => removeEventListener('scroll', f); }, []);
  useEffect(() => setOpen(false), [pathname]);
  // scroll-spy
  useEffect(() => {
    if (pathname !== '/') return;
    const ids = LINKS.map((l) => l.id).filter((i) => i !== 'top');
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) setActive(e.target.id); }), { rootMargin: '-45% 0px -50% 0px' });
    ids.forEach((id) => { const el = document.getElementById(id); if (el) io.observe(el); });
    const onTop = () => { if (window.scrollY < 200) setActive('top'); };
    addEventListener('scroll', onTop, { passive: true });
    return () => { io.disconnect(); removeEventListener('scroll', onTop); };
  }, [pathname]);

  const go = (e, l) => {
    e.preventDefault(); setOpen(false);
    const scroll = () => (l.id === 'top' ? window.scrollTo({ top: 0, behavior: 'smooth' }) : document.getElementById(l.id)?.scrollIntoView({ behavior: 'smooth' }));
    if (pathname === '/') scroll(); else { navigate('/'); setTimeout(scroll, 120); }
  };

  return (
    <>
      <nav id="nav" className={scrolled ? 's' : ''} aria-label="Primary">
        <div className="wrap">
          <Logo />
          <ul className="nav-links">
            {LINKS.map((l) => (<li key={l.id}><a href={l.to} onClick={(e) => go(e, l)} className={pathname === '/' && active === l.id ? 'active' : ''}>{l.label}</a></li>))}
          </ul>
          <div className="nav-r">
            <Link to="/dashboard" className="login-btn">Sign In</Link>
            <Button to="/chat" size="sm">Get Started <ArrowUpRight size={16} /></Button>
            <button className="burger" onClick={() => setOpen((o) => !o)} aria-label={open ? 'Close menu' : 'Open menu'} aria-expanded={open}>{open ? <X size={28} /> : <Menu size={28} />}</button>
          </div>
        </div>
      </nav>
      <div id="mobile-menu" className={open ? 'o' : ''}>
        {LINKS.map((l) => (<a key={l.id} href={l.to} onClick={(e) => go(e, l)} className={active === l.id && pathname === '/' ? 'active' : ''}>{l.label}</a>))}
        <Link to="/dashboard">Sign In</Link>
        <Link to="/chat" className="active">Get Started</Link>
      </div>
    </>
  );
}
