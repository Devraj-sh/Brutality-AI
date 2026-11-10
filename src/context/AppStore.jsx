import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { storage } from '../services/storage.js';
import { SEED_GOALS, SEED_TASKS, SEED_ACTIVITY, WEEKLY_PERFORMANCE, BASE_STATS, DEMO_USER } from '../data/mockData.js';

const Ctx = createContext(null);
export const useApp = () => useContext(Ctx);
const uid = (p) => `${p}${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
const nowLabel = () => new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });

export function AppProvider({ children }) {
  const [goals, setGoals] = useState(() => storage.get('goals', SEED_GOALS));
  const [tasks, setTasks] = useState(() => storage.get('tasks', SEED_TASKS));
  const [activity, setActivity] = useState(() => storage.get('activity', SEED_ACTIVITY));
  const [toasts, setToasts] = useState([]);
  const toastTimers = useRef([]);

  useEffect(() => storage.set('goals', goals), [goals]);
  useEffect(() => storage.set('tasks', tasks), [tasks]);
  useEffect(() => storage.set('activity', activity), [activity]);
  useEffect(() => () => toastTimers.current.forEach(clearTimeout), []);

  const toast = useCallback((message, type = 'ok') => {
    const id = uid('toast');
    setToasts((t) => [...t.slice(-2), { id, message, type }]);
    toastTimers.current.push(setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3200));
  }, []);

  const log = useCallback((type, text) => setActivity((a) => [{ id: uid('a'), type, text, time: nowLabel() }, ...a].slice(0, 30)), []);

  /* ---- tasks ---- */
  const setTaskStatus = useCallback((id, status) => {
    setTasks((ts) => ts.map((t) => (t.id === id ? { ...t, status, completedAt: status === 'done' ? nowLabel() : undefined } : t)));
    const t = tasks.find((x) => x.id === id);
    if (!t) return;
    if (status === 'done') { log('done', `Completed "${t.title}"`); toast('Marked complete. Now do the next one.'); }
    else if (status === 'missed') { log('missed', `Missed "${t.title}"`); toast('Logged as missed. No hiding from it.', 'error'); }
    else { toast('Reset to pending.'); }
  }, [tasks, log, toast]);

  const addTask = useCallback((task) => {
    const t = { id: uid('t'), status: 'pending', priority: 'medium', time: '09:00', description: '', ...task };
    setTasks((ts) => [...ts, t].sort((a, b) => a.time.localeCompare(b.time)));
    log('plan', `Committed to "${t.title}"`);
    toast('Commitment added.');
  }, [log, toast]);

  const deleteTask = useCallback((id) => { setTasks((ts) => ts.filter((t) => t.id !== id)); toast('Task removed.'); }, [toast]);

  /* ---- goals ---- */
  const saveGoal = useCallback((goal) => {
    const isNew = !goal.id;
    const g = { ...goal, id: goal.id || uid('g'), createdAt: goal.createdAt || new Date().toISOString().slice(0, 10) };
    setGoals((gs) => (isNew ? [g, ...gs] : gs.map((x) => (x.id === g.id ? g : x))));
    if (isNew) {
      // create today's tasks from the daily commitments
      const slots = ['07:00', '11:00', '16:00', '20:00'];
      const newTasks = (g.commitments || []).filter(Boolean).map((c, i) => ({
        id: uid('t'), goalId: g.id, title: c, description: `Part of your goal "${g.title}".`, time: slots[i % slots.length], priority: g.priority, status: 'pending',
      }));
      setTasks((ts) => [...ts, ...newTasks].sort((a, b) => a.time.localeCompare(b.time)));
      log('plan', `New goal committed: "${g.title}"`);
      toast('Goal created. Commitments added to your board.');
    } else toast('Goal updated.');
    return g;
  }, [log, toast]);

  const deleteGoal = useCallback((id) => {
    setGoals((gs) => gs.filter((g) => g.id !== id));
    setTasks((ts) => ts.filter((t) => t.goalId !== id));
    toast('Goal and its commitments deleted.');
  }, [toast]);

  const resetDemo = useCallback(() => {
    setGoals(SEED_GOALS); setTasks(SEED_TASKS); setActivity(SEED_ACTIVITY);
    storage.remove('chat'); storage.remove('chat-sessions');
    toast('Demo data reset.');
  }, [toast]);

  /* ---- derived ---- */
  const stats = useMemo(() => {
    const done = tasks.filter((t) => t.status === 'done').length;
    const missed = tasks.filter((t) => t.status === 'missed').length;
    const pending = tasks.length - done - missed;
    const completed = BASE_STATS.completedBefore + done;
    const missedTotal = BASE_STATS.missedBefore + missed;
    const consistency = Math.round((completed / Math.max(1, completed + missedTotal + 0)) * 100);
    const streak = missed > 0 ? 0 : BASE_STATS.streak + (done > 0 ? 1 : 0);
    const todayPct = tasks.length ? Math.round((done / tasks.length) * 100) : 0;
    return { done, missed, pending, completed, missedAll: missedTotal, todayMissed: missed, consistency, streak, todayPct, total: tasks.length };
  }, [tasks]);

  const weekly = useMemo(() => [...WEEKLY_PERFORMANCE, { day: 'Today', committed: tasks.length, completed: stats.done }].map((d) => ({ ...d, pct: d.committed ? Math.round((d.completed / d.committed) * 100) : 0 })), [tasks, stats.done]);

  const value = { user: DEMO_USER, goals, tasks, activity, stats: { ...stats, missed: stats.missedAll }, weekly, toasts,
    toast, setTaskStatus, addTask, deleteTask, saveGoal, deleteGoal, resetDemo };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
