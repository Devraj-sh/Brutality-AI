import { useEffect, useState } from 'react';
import { NavLink, Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, Plus, LayoutDashboard, Target, ListChecks, FileBarChart, History, Settings, MessagesSquare, Home, RotateCcw } from 'lucide-react';
import Logo from './Logo.jsx';
import Button from './Button.jsx';
import Modal from './Modal.jsx';
import { useApp } from '../context/AppStore.jsx';

const NAV = [
  { to: '/dashboard', label: 'Overview', I: LayoutDashboard, end: true },
  { to: '/goals', label: 'My Goals', I: Target },
  { to: '/dashboard#commitments', label: 'Daily Commitments', I: ListChecks, hash: 'commitments' },
  { to: '/reports', label: 'Reality Reports', I: FileBarChart, end: true },
  { to: '/reports?tab=history', label: 'Progress History', I: History, tab: 'history' },
];

export default function AppShell({ children, title, actions }) {
  const [open, setOpen] = useState(false);
  const [settings, setSettings] = useState(false);
  const { user, resetDemo, stats } = useApp();
  const { pathname, search, hash } = useLocation();
  const navigate = useNavigate();
  useEffect(() => setOpen(false), [pathname, search, hash]);

  const isActive = (n) => {
    if (n.hash) return pathname === '/dashboard' && hash === `#${n.hash}`;
    if (n.tab) return pathname === '/reports' && search.includes(`tab=${n.tab}`);
    if (n.to === '/dashboard') return pathname === '/dashboard' && !hash;
    if (n.to === '/reports') return pathname === '/reports' && !search.includes('tab=history');
    return pathname.startsWith(n.to);
  };

  return (
    <div className="app-shell">
      <div className={`scrim ${open ? 'on' : ''}`} onClick={() => setOpen(false)} />
      <aside className={`sidebar ${open ? 'open' : ''}`} aria-label="Application sidebar">
        <div className="sb-top"><Logo to="/" /><button className="sb-close" onClick={() => setOpen(false)} aria-label="Close sidebar"><X size={22} /></button></div>
        <Button block onClick={() => navigate('/chat?new=1')}><Plus size={18} strokeWidth={3} /> New Conversation</Button>
        <nav className="sb-nav">
          <Link to="/chat" className={`sb-link ${pathname === '/chat' ? 'active' : ''}`}><MessagesSquare size={18} />AI Chat</Link>
          {NAV.map((n) => (
            <Link key={n.label} to={n.to} className={`sb-link ${isActive(n) ? 'active' : ''}`}><n.I size={18} />{n.label}</Link>
          ))}
          <button className="sb-link" onClick={() => setSettings(true)}><Settings size={18} />Settings</button>
          <Link to="/" className="sb-link"><Home size={18} />Back to website</Link>
        </nav>
        <div className="sb-streak"><small>CURRENT STREAK</small><b className="num3d">{stats.streak}<span> days</span></b></div>
        <div className="sb-user">
          <div className="avatar">{user.initials}</div>
          <div><b>{user.name}</b><span>{user.plan}</span></div>
        </div>
      </aside>

      <div className="app-main">
        <header className="app-top">
          <button className="burger-app" onClick={() => setOpen(true)} aria-label="Open sidebar"><Menu size={24} /></button>
          {title}
          <div className="app-top-actions">{actions}</div>
        </header>
        {children}
      </div>

      <Modal open={settings} onClose={() => setSettings(false)} title="Settings">
        <div className="settings-list">
          <div className="set-row"><div><b>Demo profile</b><span>{user.name} · {user.plan} · member since {user.memberSince}</span></div></div>
          <div className="set-row"><div><b>Storage</b><span>All data lives in this browser (localStorage). Nothing is sent anywhere.</span></div></div>
          <div className="set-row"><div><b>Reset demo data</b><span>Restore the original goals, tasks, activity and chat.</span></div>
            <Button variant="red" size="sm" onClick={() => { resetDemo(); setSettings(false); navigate('/chat?new=1'); }}><RotateCcw size={14} /> Reset</Button></div>
        </div>
      </Modal>
    </div>
  );
}
