import { useEffect, useMemo, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Target, Flame, CheckCircle2, XCircle, Plus, Clock, Info, Trash2, Check, X, RotateCcw, Activity, Eye, BarChart3 } from 'lucide-react';
import AppShell from '../components/AppShell.jsx';
import Card, { StatCard } from '../components/Card.jsx';
import Button from '../components/Button.jsx';
import Meter from '../components/Meter.jsx';
import Modal from '../components/Modal.jsx';
import { DailyBars } from '../components/Charts.jsx';
import { useApp } from '../context/AppStore.jsx';

const FILTERS = [['all', 'All'], ['pending', 'Pending'], ['done', 'Completed'], ['missed', 'Missed']];

function observation(tasks, stats) {
  const pend = tasks.filter((t) => t.status === 'pending');
  const missed = tasks.filter((t) => t.status === 'missed');
  if (!tasks.length) return { head: 'No commitments today.', body: 'An empty plan is not a rest day. It is an unspoken decision to do nothing. Add at least one commitment.' };
  if (!pend.length && !missed.length) return { head: 'Everything delivered.', body: 'Every commitment is complete. This is what following through looks like. Repeat it tomorrow without needing a reminder.' };
  if (missed.length) return { head: `${missed.length} missed today.`, body: `"${missed[0].title}" is marked missed. That is a fact now. The question is not why it happened but what you will do at ${pend[0]?.time || 'the next slot'} that is different.${pend.length ? ` ${pend.length} commitment${pend.length > 1 ? 's' : ''} still open.` : ''}` };
  return { head: `${stats.done} of ${tasks.length} done. ${pend.length} to go.`, body: `Next up: "${pend[0].title}" at ${pend[0].time}. Your completion rate in the evening is lower than in the morning, so do not postpone it.` };
}

function TaskForm({ goals, onSubmit, onCancel }) {
  const [f, setF] = useState({ title: '', description: '', time: '09:00', priority: 'medium', goalId: goals[0]?.id || '' });
  const [err, setErr] = useState('');
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  return (
    <form onSubmit={(e) => { e.preventDefault(); if (!f.title.trim()) { setErr('Give the commitment a title. Vague is not allowed.'); return; } onSubmit({ ...f, title: f.title.trim() }); }} className="form-grid" noValidate>
      <label className="field">Commitment<input type="text" value={f.title} onChange={set('title')} placeholder="e.g. Solve 2 DSA problems" autoFocus />{err && <span className="err">{err}</span>}</label>
      <label className="field">Description<textarea rows={3} value={f.description} onChange={set('description')} placeholder="What does done look like?" /></label>
      <div className="form-2">
        <label className="field">Scheduled time<input type="time" value={f.time} onChange={set('time')} /></label>
        <label className="field">Priority<select value={f.priority} onChange={set('priority')}><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select></label>
      </div>
      <label className="field">Goal<select value={f.goalId} onChange={set('goalId')}>{goals.map((g) => <option key={g.id} value={g.id}>{g.title}</option>)}<option value="">No goal</option></select></label>
      <div className="form-actions"><Button variant="w" onClick={onCancel}>Cancel</Button><Button type="submit">Commit to it</Button></div>
    </form>
  );
}

export default function DashboardPage() {
  const { tasks, goals, stats, weekly, activity, setTaskStatus, addTask, deleteTask } = useApp();
  const [filter, setFilter] = useState('all');
  const [detail, setDetail] = useState(null);
  const [adding, setAdding] = useState(false);
  const { hash } = useLocation();
  const obs = useMemo(() => observation(tasks, stats), [tasks, stats]);
  const list = tasks.filter((t) => filter === 'all' || t.status === filter);
  const detailTask = tasks.find((t) => t.id === detail);
  const goalOf = (id) => goals.find((g) => g.id === id);
  const counts = { all: tasks.length, pending: stats.pending, done: stats.done, missed: stats.todayMissed };

  useEffect(() => { if (hash) setTimeout(() => document.getElementById(hash.slice(1))?.scrollIntoView({ behavior: 'smooth' }), 80); }, [hash]);

  return (
    <AppShell title={<h1 className="app-h1">Your actions. Your results.</h1>} actions={<Button size="sm" onClick={() => setAdding(true)}><Plus size={15} strokeWidth={3} /> <span className="hide-sm">Add task</span></Button>}>
      <div className="page-pad">
        <div className="stat-grid">
          <Card tone="blue" className="goal-card"><div className="stat-top"><span className="stat-label">CURRENT GOAL</span><Target size={18} /></div>
            <h3 className="goal-t">{goals[0]?.title || 'No goal set'}</h3>
            <Meter value={stats.todayPct} tone="lime" label="Today's completion" /><div className="stat-hint">{stats.todayPct}% of today delivered</div></Card>
          <StatCard label="Overall consistency" value={stats.consistency} suffix="%" icon={Activity} hint="All-time completed ÷ resolved" />
          <StatCard label="Current streak" value={stats.streak} suffix=" days" icon={Flame} tone="accent" hint={stats.streak ? 'Do not break it' : 'Broken. Start again today.'} />
          <StatCard label="Tasks completed" value={stats.completed} icon={CheckCircle2} hint={`${stats.done} today`} />
          <StatCard label="Tasks missed" value={stats.missed} icon={XCircle} tone={stats.todayMissed ? 'danger' : ''} hint={`${stats.todayMissed} today`} />
        </div>

        <div className="dash-grid">
          <div className="dash-col">
            <Card hover={false} id="commitments">
              <div className="sec-head"><h2 className="h-sm">Daily commitments</h2>
                <div className="filters" role="tablist" aria-label="Filter by status">
                  {FILTERS.map(([k, l]) => (<button key={k} role="tab" aria-selected={filter === k} className={`pill sm ${filter === k ? 'active' : ''}`} onClick={() => setFilter(k)}>{l} · {counts[k]}</button>))}
                </div>
              </div>
              <div className="task-list">
                {list.length === 0 && <div className="empty">Nothing here. {filter === 'all' ? 'Add your first commitment.' : 'Try another filter.'}</div>}
                {list.map((t) => (
                  <div key={t.id} className={`task ${t.status}`}>
                    <div className="task-time"><Clock size={14} />{t.time}</div>
                    <div className="task-main">
                      <b>{t.title}</b>
                      <p>{t.description || 'No description.'}</p>
                      <div className="task-meta">
                        <span className={`badge ${t.priority}`}>{t.priority}</span>
                        <span className={`badge ${t.status === 'pending' ? 'pending' : t.status}`}>{t.status === 'done' ? `Done${t.completedAt ? ' · ' + t.completedAt : ''}` : t.status}</span>
                        {goalOf(t.goalId) && <span className="goal-tag">{goalOf(t.goalId).title}</span>}
                      </div>
                    </div>
                    <div className="task-actions">
                      {t.status === 'pending' ? (<>
                        <Button size="sm" onClick={() => setTaskStatus(t.id, 'done')}><Check size={14} strokeWidth={3.5} /> Mark complete</Button>
                        <Button size="sm" variant="red" onClick={() => setTaskStatus(t.id, 'missed')}><X size={14} strokeWidth={3.5} /> Missed</Button>
                      </>) : (<Button size="sm" variant="w" onClick={() => setTaskStatus(t.id, 'pending')}><RotateCcw size={14} /> Undo</Button>)}
                      <Button size="sm" variant="w" icon aria-label={`Details for ${t.title}`} onClick={() => setDetail(t.id)}><Info size={16} /></Button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <Card hover={false}>
              <div className="sec-head"><h2 className="h-sm"><BarChart3 size={18} /> Weekly performance</h2></div>
              <DailyBars data={weekly} height={240} />
              <p className="chart-note">Share of commitments completed each day. Red means under 40%.</p>
            </Card>
          </div>

          <div className="dash-col">
            <Card tone="blue" hover={false} className="reality">
              <div className="stat-top"><span className="stat-label"><Eye size={14} /> TODAY&apos;S REALITY</span></div>
              <h3>{obs.head}</h3><p>{obs.body}</p><span className="agent-tag">REALITY AGENT</span>
            </Card>
            <Card hover={false}>
              <h2 className="h-sm">Recent activity</h2>
              <ul className="activity">
                {activity.slice(0, 8).map((a) => (<li key={a.id} className={a.type}><i /><span>{a.text}</span><time>{a.time}</time></li>))}
              </ul>
            </Card>
          </div>
        </div>
      </div>

      <Modal open={adding} onClose={() => setAdding(false)} title="New commitment"><TaskForm goals={goals} onCancel={() => setAdding(false)} onSubmit={(t) => { addTask(t); setAdding(false); }} /></Modal>
      <Modal open={!!detailTask} onClose={() => setDetail(null)} title={detailTask?.title || ''}>
        {detailTask && (
          <div className="detail">
            <p>{detailTask.description || 'No description.'}</p>
            <dl>
              <dt>Scheduled</dt><dd>{detailTask.time}</dd>
              <dt>Priority</dt><dd>{detailTask.priority}</dd>
              <dt>Status</dt><dd>{detailTask.status}{detailTask.completedAt ? ` at ${detailTask.completedAt}` : ''}</dd>
              <dt>Goal</dt><dd>{goalOf(detailTask.goalId)?.title || 'None'}</dd>
            </dl>
            <div className="form-actions">
              <Button variant="red" size="sm" onClick={() => { deleteTask(detailTask.id); setDetail(null); }}><Trash2 size={14} /> Delete</Button>
              {detailTask.status !== 'done' && <Button size="sm" onClick={() => { setTaskStatus(detailTask.id, 'done'); setDetail(null); }}>Mark complete</Button>}
            </div>
          </div>
        )}
      </Modal>
    </AppShell>
  );
}
