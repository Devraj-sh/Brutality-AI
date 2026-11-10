import { useEffect, useRef, useState } from 'react';
import { Target, Clock, Flag, Repeat, Zap, ShieldCheck, Bell, Check } from 'lucide-react';

const ITEMS = [
  { id: 1, t: 'Solve 2 DSA problems', time: '07:00' },
  { id: 2, t: 'Study OS · 60 min', time: '10:00' },
  { id: 3, t: 'Mock interview prep', time: '16:00' },
];

/** The Accountability Mirror: 3D stage with mouse-parallax layers (same technique as ReviewSetu). */
export default function HeroStage() {
  const stage = useRef(null);
  const [done, setDone] = useState([1, 2]);
  const pct = Math.round((done.length / ITEMS.length) * 100);
  const score = 52 + done.length * 8;

  useEffect(() => {
    const st = stage.current;
    if (!st || matchMedia('(prefers-reduced-motion: reduce)').matches || !matchMedia('(hover:hover)').matches) return;
    const layers = [...st.querySelectorAll('.layer[data-d]')];
    let raf = 0;
    const onMove = (e) => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const x = e.clientX / innerWidth - 0.5, y = e.clientY / innerHeight - 0.5;
        layers.forEach((l) => { const d = +l.dataset.d; l.style.translate = `${-x * d}px ${-y * d}px`; });
      });
    };
    addEventListener('mousemove', onMove);
    return () => { removeEventListener('mousemove', onMove); cancelAnimationFrame(raf); };
  }, []);

  const toggle = (id) => setDone((d) => (d.includes(id) ? d.filter((x) => x !== id) : [...d, id]));
  const R = 34, C = 2 * Math.PI * R;

  return (
    <div className="stage" ref={stage}>
      {/* background geometry */}
      <div className="layer geo geo-sq" data-d="6" style={{ left: '2%', top: 30 }} aria-hidden="true" />
      <div className="layer geo geo-ring" data-d="8" style={{ right: '4%', bottom: 90 }} aria-hidden="true" />
      <div className="layer geo geo-tri" data-d="12" style={{ left: '46%', top: 8 }} aria-hidden="true" />

      {/* laptop */}
      <div className="layer laptop" data-d="10" aria-label="Brutality AI accountability dashboard preview">
        <div className="lscreen">
          <i className="lside" />
          <div className="ld">
            <div className="lhead"><b>TODAY</b><span>{done.length}/{ITEMS.length} DELIVERED</span></div>
            <div className="lkpi"><div><small>CONSISTENCY</small><b>{67 + done.length * 3}%</b></div><div><small>STREAK</small><b>{4 + (done.length > 1 ? 1 : 0)}d</b></div><div><small>MISSED</small><b className="red">{ITEMS.length - done.length}</b></div></div>
            <div className="lbars">{[100, 100, 100, 50, 33, 0, pct].map((h, i) => (<s key={i} style={{ height: `${Math.max(h, 6)}%`, background: h < 40 ? 'linear-gradient(#f84848,#cb1c1c)' : undefined }} />))}</div>
          </div>
        </div>
        <div className="lbase" />
      </div>

      {/* daily commitment card (interactive) */}
      <div className="layer rev commit" data-d="26" style={{ left: 0, top: 215 }}>
        <div className="rev-title">DAILY COMMITMENTS</div>
        {ITEMS.map((i) => (
          <button key={i.id} className={`ck ${done.includes(i.id) ? 'on' : ''}`} onClick={() => toggle(i.id)} aria-pressed={done.includes(i.id)}>
            <span className="box">{done.includes(i.id) && <Check size={12} strokeWidth={4} />}</span>
            <span className="ck-t">{i.t}</span><em>{i.time}</em>
          </button>
        ))}
      </div>

      {/* progress meter */}
      <div className="layer rev meter-card" data-d="34" style={{ right: 6, top: 90 }}>
        <svg width="84" height="84" viewBox="0 0 84 84" aria-hidden="true">
          <circle cx="42" cy="42" r={R} fill="none" stroke="#e2e4f0" strokeWidth="9" />
          <circle cx="42" cy="42" r={R} fill="none" stroke="#111318" strokeWidth="9" strokeLinecap="round" strokeDasharray={C} strokeDashoffset={C * (1 - pct / 100)} transform="rotate(-90 42 42)" style={{ transition: 'stroke-dashoffset .6s ease' }} />
        </svg>
        <div className="ring-num">{pct}<small>%</small></div>
        <div className="rev-sub">COMPLETED TODAY</div>
      </div>

      {/* notification */}
      <div className="layer rev notif" data-d="40" style={{ right: 0, top: 6 }}>
        <span className="bell"><Bell size={14} /></span>
        <div><b>You committed.</b><br />Did you deliver?</div>
      </div>

      {/* reality score */}
      <div className="layer score" data-d="22" style={{ right: 30, bottom: 28 }}>
        <small>REALITY SCORE</small>
        <div className="num3d">{score}<span>/100</span></div>
        <div className="mini-meter"><i style={{ width: `${score}%` }} /></div>
      </div>

      {/* floating icon tiles */}
      {[
        { I: ShieldCheck, l: 'Discipline', s: { left: '40%', bottom: 4 }, d: 18, a: 'fl' },
        { I: Clock, l: 'Time', s: { left: '36%', top: 0 }, d: 30, a: 'fl2' },
        { I: Flag, l: 'Goals', s: { left: '-1%', bottom: 90 }, d: 20, a: 'fl' },
        { I: Repeat, l: 'Consistency', s: { right: '1%', top: 268 }, d: 16, a: 'fl2' },
        { I: Zap, l: 'Execution', s: { left: '18%', bottom: 0 }, d: 36, a: 'fl' },
      ].map(({ I, l, s, d, a }) => (
        <div key={l} className="layer itile" data-d={d} style={{ ...s, '--anim': a }} title={l}><I size={22} strokeWidth={2.6} /><span className="sr-only">{l}</span></div>
      ))}
      <div className="layer tile-target" data-d="14" style={{ left: '50%', bottom: 140 }}><Target size={26} strokeWidth={2.6} /></div>

      {/* lime stars */}
      <span className="layer star" data-d="18" style={{ left: '50%', top: 30 }} aria-hidden="true">✦</span>
      <span className="layer star s2" data-d="12" style={{ left: '4%', top: 150 }} aria-hidden="true">✦</span>
      <span className="layer star s3" data-d="22" style={{ right: '8%', bottom: 10 }} aria-hidden="true">✦</span>
      <div className="layer sticker" data-d="28" style={{ left: '30%', top: 150, fontFamily: 'var(--f-display)', fontSize: 13 }}>NO EXCUSES</div>
    </div>
  );
}
