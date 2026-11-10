import { useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, ArrowDown, Target, MessageCircle, TrendingDown, Flag, ListChecks, Zap, ScanSearch, Flame, TrendingUp, Rocket, ClipboardCheck,
  ShieldAlert, CalendarClock, FileBarChart, BrainCircuit, Download, Check, X, Quote, Eye, Repeat, Scale, Check as Tick } from 'lucide-react';
import SiteNav from '../components/SiteNav.jsx';
import SiteFooter from '../components/SiteFooter.jsx';
import HeroStage from '../components/HeroStage.jsx';
import Button from '../components/Button.jsx';
import Card from '../components/Card.jsx';
import Meter from '../components/Meter.jsx';
import ReportCard from '../components/ReportCard.jsx';
import { DailyBars } from '../components/Charts.jsx';
import { useApp } from '../context/AppStore.jsx';
import { useRevealOnScroll, useCounter } from '../hooks/useReveal.js';
import { AGENTS, SEED_REPORTS } from '../data/mockData.js';
import { printElement } from '../utils.js';

const AGENT_ICONS = { onboarding: Rocket, checkin: ClipboardCheck, confront: ShieldAlert, planner: CalendarClock, reality: FileBarChart, memory: BrainCircuit };

const PROCESS = [
  { k: 'Goal', I: Flag, d: 'Define the outcome you actually want, in plain words.', tone: '' },
  { k: 'Commitment', I: ListChecks, d: 'Turn it into measurable daily tasks with times.', tone: 'soft' },
  { k: 'Action', I: Zap, d: 'You do the work. The clock is already running.', tone: 'blue' },
  { k: 'Verification', I: ScanSearch, d: 'You report what really happened. Evidence, not feelings.', tone: '' },
  { k: 'Confrontation', I: Flame, d: 'Vague answers and repeat excuses get challenged.', tone: 'danger' },
  { k: 'Improvement', I: TrendingUp, d: 'The plan adapts to your real performance.', tone: 'accent' },
];

function Counter({ to, suffix = '' }) { const ref = useCounter(to); return <><span ref={ref}>0</span>{suffix}</>; }

function Hero() {
  return (
    <div className="hero-container on-blue" id="top">
      <div className="wrap hero">
        <div>
          <span className="eyebrow">THE PERSONAL ACCOUNTABILITY ENGINE</span>
          <h1>You don&apos;t need more motivation.<br />You need <span className="hl">accountability.</span></h1>
          <p>You already know what you need to do. The problem is following through. Brutality AI tracks your commitments, challenges your excuses and makes sure your actions match your ambitions.</p>
          <div className="row">
            <Button to="/chat" className="lg">Start your accountability journey <ArrowRight size={18} /></Button>
            <Button variant="w" className="lg" onClick={() => document.getElementById('how')?.scrollIntoView({ behavior: 'smooth' })}>Explore how it works <ArrowDown size={18} /></Button>
          </div>
          <div className="trust"><span className="dot" />Built for people who are serious about their goals.</div>
        </div>
        <HeroStage />
      </div>
    </div>
  );
}

function Problem() {
  const items = [
    { I: Target, t: 'The Promise', p: 'Every Monday starts with a new plan. Every Friday ends with another excuse.' },
    { I: MessageCircle, t: 'The Excuse', p: "'Tomorrow', 'No time', 'Not in the mood'. The same excuses keep repeating." },
    { I: TrendingDown, t: 'The Result', p: 'Unfinished goals. Broken consistency. Lost confidence.', tone: 'blue' },
  ];
  return (
    <section className="page-section" id="problem">
      <div className="wrap">
        <div className="reveal"><span className="eyebrow">THE PROBLEM</span><h2 className="section-title" style={{ maxWidth: 900 }}>You know what to do. So why aren&apos;t you doing it?</h2></div>
        <div className="grid3">
          {items.map((c, i) => (
            <Card key={c.t} tone={c.tone} className={`reveal big-card`} style={{ transitionDelay: `${i * 90}ms` }}>
              <div className={`icon-tile ${c.tone ? 'lime' : ''}`}><c.I size={30} strokeWidth={2.4} /></div>
              <div className="card-no num3d">0{i + 1}</div>
              <h3>{c.t}</h3><p>{c.p}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

function Theory() {
  const reqs = [
    { I: Target, t: 'A clear commitment', p: 'Specific, measurable, with a time attached. "Get fit" is not one. "Gym, 6 PM, four days" is.' },
    { I: Eye, t: 'Honest evaluation', p: 'Looking at what you actually did, not what you meant to do or what you feel you did.' },
    { I: Repeat, t: 'Consistent correction', p: 'Small, repeated adjustments. The plan changes. The standard does not.' },
  ];
  return (
    <section className="page-section on-deep theory" id="theory">
      <div className="wrap">
        <div className="reveal">
          <span className="eyebrow">ACCOUNTABILITY THEORY</span>
          <h2 className="section-title" style={{ color: '#fff', maxWidth: 900 }}>The science of holding yourself accountable.</h2>
          <p className="section-desc" style={{ maxWidth: 760 }}>
            The product is built on the <b>Accountability Mirror</b>, a practice popularised by David Goggins: stand in front of a mirror, say plainly what you have been avoiding, and face the gap between who you claim to be and what you do. Radical self-honesty, on a schedule.
          </p>
        </div>
        <div className="grid3 reveal">
          {reqs.map((r, i) => (
            <div key={r.t} className="theory-req"><span className="num3d">{i + 1}</span><r.I size={22} /><h4>{r.t}</h4><p>{r.p}</p></div>
          ))}
        </div>
        <p className="reveal theory-lead">Brutality AI operationalises this idea as a loop, run every day by AI agents that never get tired of asking the same question:</p>
        <div className="proc reveal" role="list" aria-label="The accountability loop">
          {PROCESS.map((s, i) => (
            <motion.div key={s.k} role="listitem" className={`proc-card tactile-card ${s.tone}`} whileHover={{ rotateX: -6, rotateY: 6, y: -6 }} transition={{ type: 'spring', stiffness: 260, damping: 18 }}>
              <div className="proc-n">0{i + 1}</div>
              <div className="icon-tile sm"><s.I size={22} strokeWidth={2.5} /></div>
              <h4>{s.k}</h4><p>{s.d}</p>
              {i < PROCESS.length - 1 && <span className="conn" aria-hidden="true"><i /></span>}
            </motion.div>
          ))}
        </div>
        <div className="statement reveal"><Quote size={26} /><span>Your excuses don&apos;t change your commitments.</span></div>
        <p className="disclaimer reveal">This is the behavioural philosophy behind the product, not a scientifically proven guarantee of results. Brutality means honest, evidence-based accountability. Never insults or humiliation.</p>
      </div>
    </section>
  );
}

function How() {
  const steps = [
    { n: '01', t: 'Set your goal', p: 'Tell Brutality AI what you want to achieve.', ex: <q>Prepare for my upcoming placement interviews.</q> },
    { n: '02', t: 'Commit to the plan', p: 'The AI breaks your goal into measurable daily tasks.', ex: <ul><li>Solve 2 DSA problems.</li><li>Study for 90 minutes.</li><li>Revise one CS fundamental.</li></ul>, tone: 'blue' },
    { n: '03', t: 'Face the reality', p: 'Report what you actually completed. Brutality AI analyses your response, confronts vague excuses and updates your plan.', ex: <q>I did 1 problem. No time for the rest.<br /><b className="warn">“No time” again? You scrolled 94 minutes yesterday.</b></q>, tone: 'accent' },
  ];
  return (
    <section className="page-section" id="how">
      <div className="wrap">
        <div className="reveal"><span className="eyebrow">HOW IT WORKS</span><h2 className="section-title">From ambition to execution.</h2></div>
        <div className="steps">
          {steps.map((s, i) => (
            <div key={s.n} className="step-wrap reveal" style={{ transitionDelay: `${i * 100}ms` }}>
              <Card tone={s.tone} className="step-card">
                <div className="step-n num3d">{s.n}</div>
                <h3>{s.t}</h3><p>{s.p}</p>
                <div className="step-ex">{s.ex}</div>
              </Card>
              {i < 2 && <span className="step-arrow" aria-hidden="true"><ArrowRight size={34} strokeWidth={3} /></span>}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Agents() {
  return (
    <section className="page-section agents" id="agents">
      <div className="wrap">
        <div className="reveal"><span className="eyebrow">THE TEAM</span><h2 className="section-title" style={{ maxWidth: 900 }}>Six agents. One mission. Your accountability.</h2></div>
        <div className="grid-agents">
          {AGENTS.map((a, i) => {
            const I = AGENT_ICONS[a.key];
            return (
              <motion.div key={a.key} className="reveal" style={{ transitionDelay: `${(i % 3) * 80}ms` }} whileHover={{ y: -6 }}>
                <Card tone={i === 2 ? 'blue' : i === 4 ? 'accent' : ''} className="agent-card" tabIndex={0}>
                  <div className="agent-top"><span className="agent-n num3d">{a.n}</span><div className="icon-tile sm"><I size={24} strokeWidth={2.4} /></div></div>
                  <h3>{a.name}</h3>
                  <p>{a.blurb}</p>
                  <div className="agent-more"><p>{a.detail}</p></div>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function Preview() {
  const { tasks, stats, goals, activity, weekly, setTaskStatus } = useApp();
  const shown = tasks.slice(0, 5);
  return (
    <section className="page-section on-blue preview" id="preview">
      <div className="wrap">
        <div className="reveal"><span className="eyebrow">PRODUCT PREVIEW</span><h2 className="section-title" style={{ color: '#fff', maxWidth: 800 }}>This is what accountability looks like.</h2>
          <p className="section-desc">It is live: tick a task and watch the numbers move.</p></div>
        <div className="browser reveal">
          <div className="browser-bar"><i /><i /><i /><span>brutality.ai/dashboard</span></div>
          <div className="pv-body">
            <div className="pv-goal"><small>CURRENT GOAL</small><b>{goals[0]?.title || 'No goal set'}</b><Meter value={stats.todayPct} tone="lime" label="Today's progress" /></div>
            <div className="pv-stats">
              <div className="tactile-card flat"><small>CONSISTENCY</small><b className="num3d">{stats.consistency}%</b></div>
              <div className="tactile-card flat accent"><small>COMPLETED</small><b className="num3d">{stats.completed}</b></div>
              <div className="tactile-card flat danger"><small>MISSED</small><b className="num3d">{stats.missed}</b></div>
              <div className="tactile-card flat"><small>STREAK</small><b className="num3d">{stats.streak}d</b></div>
            </div>
            <div className="tactile-card flat pv-tasks">
              <h4>Daily commitments</h4>
              {shown.map((t) => (
                <div key={t.id} className={`pv-task ${t.status}`}>
                  <button className="ck-box" aria-label={`${t.status === 'done' ? 'Undo' : 'Complete'} ${t.title}`} onClick={() => setTaskStatus(t.id, t.status === 'done' ? 'pending' : 'done')}>{t.status === 'done' && <Check size={14} strokeWidth={4} />}{t.status === 'missed' && <X size={14} strokeWidth={4} />}</button>
                  <span>{t.title}</span><em>{t.time}</em>
                </div>
              ))}
            </div>
            <div className="tactile-card flat pv-chart"><h4>Weekly performance</h4><DailyBars data={weekly} height={170} /></div>
            <div className="tactile-card flat pv-ai"><span className="agent-tag">CONFRONT AGENT</span><p>“You missed leg day and wrote ‘no time’. Your phone says 94 minutes on social apps yesterday. Which one is the real reason?”</p></div>
            <div className="tactile-card flat pv-recent"><h4>Recent check-ins</h4>{activity.slice(0, 4).map((a) => (<div key={a.id} className={`pv-act ${a.type}`}><i />{a.text}<em>{a.time}</em></div>))}</div>
          </div>
        </div>
        <div className="center reveal"><Button to="/dashboard" className="lg">Open the full dashboard <ArrowRight size={18} /></Button></div>
      </div>
    </section>
  );
}

function Report() {
  const navigate = useNavigate();
  const { toast } = useApp();
  const ref = useRef(null);
  const r = SEED_REPORTS[0];
  return (
    <section className="page-section" id="report">
      <div className="wrap">
        <div className="reveal"><span className="eyebrow">REALITY REPORT</span><h2 className="section-title">No sugarcoating. Just the reality.</h2>
          <p className="section-desc">Every week, the Reality Agent audits what you promised against what you delivered.</p></div>
        <div className="report-wrap reveal">
          <ReportCard report={r} ref={ref} />
          <div className="report-actions">
            <Button className="lg" onClick={() => { toast('Opening print dialog. Choose "Save as PDF".'); printElement(ref.current); }}><Download size={18} /> Download report</Button>
            <Button variant="w" className="lg" onClick={() => navigate('/reports')}>See all reports <ArrowRight size={18} /></Button>
          </div>
        </div>
      </div>
    </section>
  );
}

function Pricing() {
  const { toast } = useApp();
  const navigate = useNavigate();
  const plans = [
    { n: 'Starter', p: '₹0', per: 'forever', f: ['1 active goal', 'Daily check-in chat', 'Basic weekly summary'], b: 'Start free', v: 'w' },
    { n: 'Pro', p: '₹399', per: '/ month', f: ['Unlimited goals', 'All six AI agents', 'Weekly Reality Reports', 'Excuse-pattern analysis'], b: 'Go Pro', hot: true },
    { n: 'Team', p: '₹1,499', per: '/ month', f: ['Up to 10 people', 'Shared accountability board', 'Team Reality Reports'], b: 'Talk to us', v: 'w' },
  ];
  return (
    <section className="page-section pricing" id="pricing">
      <div className="wrap">
        <div className="reveal"><span className="eyebrow">PRICING</span><h2 className="section-title">Cheaper than another unfinished plan.</h2><p className="section-desc">Demo pricing. No payment is collected in this frontend build.</p></div>
        <div className="grid3">
          {plans.map((pl, i) => (
            <Card key={pl.n} tone={pl.hot ? 'blue' : ''} className="reveal plan" style={{ transitionDelay: `${i * 90}ms` }}>
              {pl.hot && <span className="sticker plan-sticker">MOST CHOSEN</span>}
              <h3>{pl.n}</h3>
              <div className="plan-price num3d">{pl.p}<small>{pl.per}</small></div>
              <ul>{pl.f.map((x) => <li key={x}><Tick size={16} strokeWidth={3.5} />{x}</li>)}</ul>
              <Button variant={pl.v || ''} block onClick={() => { toast(`${pl.n} selected (demo). Taking you to the chat.`); setTimeout(() => navigate('/chat'), 700); }}>{pl.b}</Button>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

function FinalCTA() {
  return (
    <section className="cta on-lime">
      <div className="wrap center">
        <h2>Stop negotiating with your excuses.</h2>
        <p>Your goals deserve more than another unfinished plan.</p>
        <Button variant="blue" className="lg" to="/chat">Start with Brutality AI <ArrowRight size={18} /></Button>
      </div>
    </section>
  );
}

export default function HomePage() {
  useRevealOnScroll();
  const stats = useMemo(() => [{ n: 6, s: '', l: 'AI agents on your side' }, { n: 3, s: '', l: 'steps from goal to execution' }, { n: 7, s: '', l: 'days, then one honest Reality Report' }], []);
  return (
    <>
      <SiteNav />
      <main>
        <Hero />
        <div className="stat-strip"><div className="wrap strip-grid">{stats.map((s) => (<div key={s.l}><b className="num3d"><Counter to={s.n} suffix={s.s} /></b><span>{s.l}</span></div>))}</div></div>
        <Problem /><Theory /><How /><Agents /><Preview /><Report /><Pricing /><FinalCTA />
      </main>
      <SiteFooter />
    </>
  );
}
