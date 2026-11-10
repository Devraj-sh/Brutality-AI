/** Print only one element (used by "Download Report"). Uses the browser print dialog -> Save as PDF. */
export function printElement(el) {
  if (!el) { window.print(); return; }
  el.classList.add('print-target');
  document.body.classList.add('print-one');
  const cleanup = () => { el.classList.remove('print-target'); document.body.classList.remove('print-one'); removeEventListener('afterprint', cleanup); };
  addEventListener('afterprint', cleanup);
  setTimeout(() => window.print(), 50);
}
export const pctColor = (p) => (p >= 75 ? '#111318' : p >= 40 ? '#878d9f' : '#E52929');
export const fmtDate = (d) => new Date(d + 'T00:00:00').toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
