import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { pctColor } from '../utils.js';

const axis = { fontFamily: 'Space Grotesk', fontSize: 11, fontWeight: 700, fill: '#737989' };
const tip = { contentStyle: { borderRadius: 12, border: '1.5px solid #111318', fontFamily: 'Space Grotesk', fontWeight: 700, fontSize: 12, boxShadow: '0 3px 0 #111318' }, cursor: { fill: 'rgba(17,19,24,.06)' } };

/** Per-day completion % bar chart. Red < 40, neutral slate 40–74, pitch black >= 75. */
export function DailyBars({ data, height = 220, xKey = 'day', yKey = 'pct' }) {
  return (
    <div role="img" aria-label="Daily completion percentage chart" style={{ width: '100%', height }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 8, right: 4, left: -22, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke="#e2e4f0" strokeDasharray="3 4" />
          <XAxis dataKey={xKey} tick={axis} axisLine={false} tickLine={false} />
          <YAxis domain={[0, 100]} ticks={[0, 50, 100]} tick={axis} axisLine={false} tickLine={false} unit="%" />
          <Tooltip {...tip} formatter={(v) => [`${v}%`, 'Completed']} />
          <Bar dataKey={yKey} radius={[7, 7, 0, 0]} maxBarSize={38} animationDuration={900}>
            {data.map((d, i) => <Cell key={i} fill={pctColor(d[yKey])} stroke="#000000" strokeWidth={d[yKey] ? 1.5 : 0} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ConsistencyLine({ data, height = 220 }) {
  return (
    <div role="img" aria-label="Consistency score history" style={{ width: '100%', height }}>
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 10, right: 12, left: -22, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke="#e2e4f0" strokeDasharray="3 4" />
          <XAxis dataKey="week" tick={axis} axisLine={false} tickLine={false} />
          <YAxis domain={[0, 100]} ticks={[0, 50, 100]} tick={axis} axisLine={false} tickLine={false} unit="%" />
          <Tooltip {...tip} formatter={(v) => [`${v}%`, 'Consistency']} />
          <Line type="monotone" dataKey="score" stroke="#111318" strokeWidth={4} dot={{ r: 6, fill: '#D6FF3D', stroke: '#111318', strokeWidth: 2 }} activeDot={{ r: 8, fill: '#D6FF3D', stroke: '#000', strokeWidth: 3 }} animationDuration={1000} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
