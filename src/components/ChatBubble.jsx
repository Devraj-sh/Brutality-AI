import { Link } from 'react-router-dom';
import { Bot, ArrowRight, FileText, Paperclip, Plus } from 'lucide-react';
import Meter from './Meter.jsx';

export function TypingIndicator() {
  return (
    <div className="msg ai" aria-live="polite" aria-label="Brutality AI is typing">
      <div className="agent-av"><Bot size={18} /></div>
      <div className="bubble ai typing"><i /><i /><i /></div>
    </div>
  );
}

function Card({ card, onAddGoal }) {
  if (!card) return null;
  if (card.kind === 'tasks') return (
    <div className="mcard"><div className="mc-row"><span className="badge done">{card.done} done</span><span className="badge missed">{card.missed} missed</span><span className="badge pending">{card.pending} pending</span></div>
      <Link to="/dashboard#commitments" className="mc-link">Open Daily Commitments <ArrowRight size={14} /></Link></div>
  );
  if (card.kind === 'progress') return (<div className="mcard"><small>CONSISTENCY</small><Meter value={card.pct} tone={card.pct >= 70 ? '' : 'red'} label="Consistency" /><Link to="/dashboard" className="mc-link">View dashboard <ArrowRight size={14} /></Link></div>);
  if (card.kind === 'report') return (<div className="mcard"><div className="mc-row"><FileText size={18} /><b>Reality Report · Week 6</b></div><Link to="/reports" className="mc-link">Open full report <ArrowRight size={14} /></Link></div>);
  if (card.kind === 'excuses') return (<div className="mcard">{[['No time', 11], ['Too tired', 6], ['Tomorrow', 5], ['Not in the mood', 3]].map(([l, n]) => (<div key={l} className="excuse-row"><span>{l}</span><Meter value={(n / 11) * 100} tone={n === 11 ? 'red' : ''} label={l} /><b>×{n}</b></div>))}</div>);
  if (card.kind === 'commit') return (<div className="mcard"><button className="btn sm" onClick={onAddGoal}><Plus size={14} strokeWidth={3} /> Add this to my goals</button></div>);
  return null;
}

export default function ChatBubble({ msg, onAddGoal }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`msg ${isUser ? 'user' : 'ai'}`}>
      {!isUser && <div className="agent-av" aria-hidden="true"><Bot size={18} /></div>}
      <div className="msg-col">
        {!isUser && <div className="agent-label"><span className="dot-live" />BRUTALITY AI · {msg.agent || 'Accountability Agent'}</div>}
        <div className={`bubble ${isUser ? 'user' : 'ai'}`}>
          {msg.attachment && <div className="attach-chip"><Paperclip size={13} />{msg.attachment}</div>}
          {msg.text.split('\n').map((l, i) => (l.trim() === '' ? <div key={i} className="gap" /> : <p key={i}>{l}</p>))}
        </div>
        {!isUser && <Card card={msg.card} onAddGoal={onAddGoal} />}
        <time className="msg-time">{msg.time}</time>
      </div>
    </div>
  );
}
