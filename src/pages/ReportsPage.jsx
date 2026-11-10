import { useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Download, Printer, FileBarChart, History as HistoryIcon, Lightbulb, XCircle } from 'lucide-react';
import AppShell from '../components/AppShell.jsx';
import Card from '../components/Card.jsx';
import Button from '../components/Button.jsx';
import Meter from '../components/Meter.jsx';
import ReportCard from '../components/ReportCard.jsx';
import { ConsistencyLine } from '../components/Charts.jsx';
import { reportService } from '../services/api.js';
import { useApp } from '../context/AppStore.jsx';
import { printElement } from '../utils.js';

export default function ReportsPage() {
  const [params, setParams] = useSearchParams();
  const tab = params.get('tab') === 'history' ? 'history' : 'reports';
  const [reports, setReports] = useState([]);
  const [history, setHistory] = useState([]);
  const [selected, setSelected] = useState('r4');
  const ref = useRef(null);
  const { toast } = useApp();

  useEffect(() => { let live = true; Promise.all([reportService.list(), reportService.history()]).then(([r, h]) => { if (live) { setReports(r); setHistory(h); } }); return () => { live = false; }; }, []);

  const report = reports.find((r) => r.id === selected) || reports[0];
  const agg = useMemo(() => {
    const ex = {}; const missed = [];
    reports.forEach((r) => { r.excuses.forEach((e) => { ex[e.label] = (ex[e.label] || 0) + e.count; }); missed.push(...r.missedList.map((m) => ({ m, w: r.label }))); });
    return { excuses: Object.entries(ex).sort((a, b) => b[1] - a[1]), missed: missed.slice(0, 10) };
  }, [reports]);

  const download = () => { toast('Opening print dialog. Choose "Save as PDF".'); printElement(ref.current); };
  const setTab = (t) => setParams(t === 'history' ? { tab: 'history' } : {});
  const maxEx = agg.excuses[0]?.[1] || 1;

  return (
    <AppShell title={<h1 className="app-h1">Reality reports</h1>}
      actions={tab === 'reports' && <Button size="sm" onClick={download}><Download size={15} /> <span className="hide-sm">Download PDF</span></Button>}>
      <div className="page-pad">
        <div className="filters tabs" role="tablist">
          <button role="tab" aria-selected={tab === 'reports'} className={`pill ${tab === 'reports' ? 'active' : ''}`} onClick={() => setTab('reports')}><FileBarChart size={15} /> Weekly reports</button>
          <button role="tab" aria-selected={tab === 'history'} className={`pill ${tab === 'history' ? 'active' : ''}`} onClick={() => setTab('history')}><HistoryIcon size={15} /> Consistency history</button>
        </div>

        {tab === 'reports' && report && (
          <div className="rep-layout">
            <div className="rep-list" role="listbox" aria-label="Previous weekly reports">
              {reports.map((r) => (
                <button key={r.id} role="option" aria-selected={selected === r.id} className={`rep-item tactile-card flat ${selected === r.id ? 'sel' : ''}`} onClick={() => setSelected(r.id)}>
                  <div><small>{r.label}</small><b>{r.week}</b></div>
                  <span className={`score-chip ${r.score >= 70 ? 'good' : r.score >= 50 ? 'mid' : 'bad'}`}>{r.score}%</span>
                </button>
              ))}
            </div>
            <div className="rep-detail">
              <ReportCard report={report} detailed ref={ref} />
              <div className="report-actions">
                <Button className="lg" onClick={download}><Download size={18} /> Download PDF</Button>
                <Button variant="w" className="lg" onClick={() => { toast('Printing the report…'); printElement(ref.current); }}><Printer size={18} /> Print</Button>
              </div>
            </div>
          </div>
        )}

        {tab === 'history' && (
          <div className="hist-grid">
            <Card hover={false} className="span2"><h2 className="h-sm">Consistency history</h2><ConsistencyLine data={history} height={260} />
              <p className="chart-note">From 38% to 67% in six weeks. Week 6 slipped from Week 5&apos;s peak of 78%.</p></Card>
            <Card hover={false}><h2 className="h-sm">Excuse patterns (all weeks)</h2>
              <div className="excuse-list">{agg.excuses.map(([l, n]) => (<div key={l} className="excuse-row"><span>“{l}”</span><Meter value={(n / maxEx) * 100} tone={n === maxEx ? 'red' : ''} label={l} /><b>×{n}</b></div>))}</div></Card>
            <Card hover={false}><h2 className="h-sm"><XCircle size={16} /> Recent missed commitments</h2>
              <ul className="rc-missed">{agg.missed.map((x) => <li key={x.m}>{x.m} <em>{x.w}</em></li>)}</ul></Card>
            <Card tone="accent" hover={false} className="span2"><h2 className="h-sm"><Lightbulb size={18} /> Improvement suggestions</h2>
              <ol className="rc-plan">
                {['Your weakest period is the evening. Schedule critical tasks before noon.', '"No time" is your most common excuse (17 mentions). Audit one day of real time use.', 'Do not raise your workload until you have five consecutive 100% days.', 'Weekends are consistently below weekdays. Treat Saturday as a working day for your goals.'].map((a, i) => (<li key={a}><b className="num3d">{i + 1}</b><span>{a}</span></li>))}
              </ol></Card>
          </div>
        )}
      </div>
    </AppShell>
  );
}
