import { useState } from 'react';
import { Plus, Pencil, Trash2, CalendarDays, ChevronRight, ChevronLeft, X, Target as TargetIcon, Flag } from 'lucide-react';
import AppShell from '../components/AppShell.jsx';
import Card from '../components/Card.jsx';
import Button from '../components/Button.jsx';
import Meter from '../components/Meter.jsx';
import Modal from '../components/Modal.jsx';
import { useApp } from '../context/AppStore.jsx';
import { fmtDate } from '../utils.js';

const STEPS = ['The goal', 'The deadline', 'Daily commitments', 'Review'];
const blank = () => ({ title: '', description: '', targetDate: new Date(Date.now() + 56 * 864e5).toISOString().slice(0, 10), priority: 'medium', commitments: [''] });
const daysLeft = (d) => Math.ceil((new Date(d + 'T23:59:59') - Date.now()) / 864e5);

function GoalWizard({ initial, onClose, onSave }) {
  const [step, setStep] = useState(0);
  const [g, setG] = useState(initial);
  const [err, setErr] = useState('');
  const set = (k) => (e) => setG({ ...g, [k]: e.target.value });
  const clean = g.commitments.map((c) => c.trim()).filter(Boolean);

  const next = () => {
    if (step === 0 && !g.title.trim()) return setErr('Name the goal. "Do better" does not count.');
    if (step === 1 && !g.targetDate) return setErr('Pick a target date. A goal without a date is a wish.');
    if (step === 2 && clean.length === 0) return setErr('Add at least one daily commitment.');
    setErr(''); setStep(step + 1);
  };
  const setC = (i, v) => setG({ ...g, commitments: g.commitments.map((c, j) => (j === i ? v : c)) });

  return (
    <div>
      <ol className="steps-bar" aria-label="Progress">{STEPS.map((s, i) => (<li key={s} className={i === step ? 'on' : i < step ? 'done' : ''}><b>{i + 1}</b><span>{s}</span></li>))}</ol>
      {step === 0 && (<div className="form-grid">
        <label className="field">Goal title<input type="text" autoFocus value={g.title} onChange={set('title')} placeholder="e.g. Become placement-ready" /></label>
        <label className="field">Description<textarea rows={3} value={g.description} onChange={set('description')} placeholder="Why does this matter, and what does success look like?" /></label>
      </div>)}
      {step === 1 && (<div className="form-grid form-2">
        <label className="field">Target date<input type="date" value={g.targetDate} onChange={set('targetDate')} /></label>
        <label className="field">Priority<select value={g.priority} onChange={set('priority')}><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select></label>
      </div>)}
      {step === 2 && (<div className="form-grid">
        <p className="muted">Break it into things you can do and verify daily.</p>
        {g.commitments.map((c, i) => (
          <div key={i} className="commit-row"><input type="text" value={c} onChange={(e) => setC(i, e.target.value)} placeholder={['Solve 2 DSA problems', 'Study core CS for 1 hour', 'Spend 30 min on interview prep'][i] || 'Another daily commitment'} aria-label={`Commitment ${i + 1}`} />
            {g.commitments.length > 1 && <Button variant="w" size="sm" icon aria-label="Remove commitment" onClick={() => setG({ ...g, commitments: g.commitments.filter((_, j) => j !== i) })}><X size={16} /></Button>}</div>
        ))}
        {g.commitments.length < 6 && <Button variant="w" size="sm" onClick={() => setG({ ...g, commitments: [...g.commitments, ''] })}><Plus size={14} /> Add commitment</Button>}
      </div>)}
      {step === 3 && (<div className="review">
        <h4>{g.title}</h4><p>{g.description || 'No description.'}</p>
        <div className="task-meta"><span className={`badge ${g.priority}`}>{g.priority}</span><span className="goal-tag">By {fmtDate(g.targetDate)}</span></div>
        <ul>{clean.map((c) => <li key={c}>{c}</li>)}</ul>
        {!initial.id && <p className="muted">These will be added to today&apos;s commitments.</p>}
      </div>)}
      {err && <p className="err">{err}</p>}
      <div className="form-actions between">
        {step > 0 ? <Button variant="w" onClick={() => { setErr(''); setStep(step - 1); }}><ChevronLeft size={16} /> Back</Button> : <Button variant="w" onClick={onClose}>Cancel</Button>}
        {step < 3 ? <Button onClick={next}>Next <ChevronRight size={16} /></Button> : <Button onClick={() => onSave({ ...g, title: g.title.trim(), commitments: clean })}>{initial.id ? 'Save changes' : 'Commit to this goal'}</Button>}
      </div>
    </div>
  );
}

export default function GoalsPage() {
  const { goals, tasks, saveGoal, deleteGoal } = useApp();
  const [wizard, setWizard] = useState(null); // goal object or {} for new
  const [toDelete, setToDelete] = useState(null);

  const progress = (g) => { const ts = tasks.filter((t) => t.goalId === g.id); return ts.length ? Math.round((ts.filter((t) => t.status === 'done').length / ts.length) * 100) : 0; };

  return (
    <AppShell title={<h1 className="app-h1">Goals &amp; planning</h1>} actions={<Button size="sm" onClick={() => setWizard(blank())}><Plus size={15} strokeWidth={3} /> <span className="hide-sm">New goal</span></Button>}>
      <div className="page-pad">
        {goals.length === 0 ? (
          <Card hover={false} className="empty-big"><Flag size={40} /><h3>No goals. No accountability.</h3><p>Commit to one real goal and I will build the daily plan.</p><Button onClick={() => setWizard(blank())}>Create your first goal</Button></Card>
        ) : (
          <div className="goal-grid">
            {goals.map((g, i) => {
              const p = progress(g); const dl = daysLeft(g.targetDate);
              return (
                <Card key={g.id} tone={i === 0 ? 'blue' : ''} className="goal-item">
                  <div className="goal-head"><span className={`badge ${g.priority}`}>{g.priority} priority</span>
                    <div className="goal-ctl">
                      <button onClick={() => setWizard(g)} aria-label={`Edit ${g.title}`}><Pencil size={16} /></button>
                      <button onClick={() => setToDelete(g)} aria-label={`Delete ${g.title}`}><Trash2 size={16} /></button>
                    </div></div>
                  <h3>{g.title}</h3>
                  <p className="goal-desc">{g.description}</p>
                  <div className="goal-date"><CalendarDays size={15} />{fmtDate(g.targetDate)} · {dl >= 0 ? `${dl} days left` : `${-dl} days overdue`}</div>
                  <div className="prog-row"><span>Progress today</span><b>{p}%</b></div>
                  <Meter value={p} tone={i === 0 ? 'lime' : ''} label={`${g.title} progress`} />
                  <h4 className="dc-h">Daily commitments</h4>
                  <ul className="dc-list">{g.commitments.map((c) => <li key={c}><TargetIcon size={14} />{c}</li>)}</ul>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      <Modal open={!!wizard} onClose={() => setWizard(null)} title={wizard?.id ? 'Edit goal' : 'Create a goal'}>
        {wizard && <GoalWizard key={wizard.id || 'new'} initial={wizard} onClose={() => setWizard(null)} onSave={(g) => { saveGoal(g); setWizard(null); }} />}
      </Modal>
      <Modal open={!!toDelete} onClose={() => setToDelete(null)} title="Delete this goal?">
        <p>&quot;{toDelete?.title}&quot; and its commitments will be removed. Are you quitting, or restructuring?</p>
        <div className="form-actions"><Button variant="w" onClick={() => setToDelete(null)}>Keep it</Button><Button variant="red" onClick={() => { deleteGoal(toDelete.id); setToDelete(null); }}>Delete goal</Button></div>
      </Modal>
    </AppShell>
  );
}
