import { Link, useNavigate } from 'react-router-dom';
import Logo from './Logo.jsx';
import { useApp } from '../context/AppStore.jsx';

export default function SiteFooter() {
  const { toast } = useApp();
  const nav = useNavigate();
  const jump = (id) => (e) => { e.preventDefault(); document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' }); };
  return (
    <footer className="site-footer on-deep">
      <div className="wrap foot-grid">
        <div>
          <Logo />
          <p className="foot-desc">An AI that remembers what you promised, tracks what you delivered, and confronts the gap.</p>
          <p className="foot-tag">STOP LYING TO YOURSELF. START DELIVERING.</p>
        </div>
        <div><h4>Navigate</h4>
          <a href="#top" onClick={(e) => { e.preventDefault(); scrollTo({ top: 0, behavior: 'smooth' }); }}>Home</a>
          <a href="#how" onClick={jump('how')}>How It Works</a>
          <a href="#theory" onClick={jump('theory')}>Accountability Theory</a>
          <a href="#pricing" onClick={jump('pricing')}>Pricing</a>
        </div>
        <div><h4>Features</h4>
          <Link to="/chat">AI Chat</Link><Link to="/dashboard">Dashboard</Link><Link to="/goals">Goals &amp; Planning</Link><Link to="/reports">Reality Reports</Link>
        </div>
        <div><h4>Company</h4>
          <a href="mailto:hello@brutality.ai" onClick={() => toast('Opening your mail app: hello@brutality.ai')}>Contact</a>
          <button className="foot-link" onClick={() => nav('/legal/privacy')}>Privacy Policy</button>
          <button className="foot-link" onClick={() => nav('/legal/terms')}>Terms of Service</button>
        </div>
      </div>
      <div className="wrap foot-bottom"><span>© 2026 Brutality AI. Frontend demo — no data leaves your browser.</span><span>Built for people who are serious about their goals.</span></div>
    </footer>
  );
}
