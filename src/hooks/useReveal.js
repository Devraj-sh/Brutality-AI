import { useEffect, useRef } from 'react';
/** Adds `.in` to any `.reveal` element when it scrolls into view. */
export function useRevealOnScroll() {
  useEffect(() => {
    const els = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) { els.forEach((e) => e.classList.add('in')); return; }
    const io = new IntersectionObserver((entries) => entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    els.forEach((e) => io.observe(e));
    return () => io.disconnect();
  });
}
export function useCounter(target, duration = 1200) {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current; if (!el) return;
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) { el.textContent = target; return; }
    let raf; let started = false;
    const run = () => { const t0 = performance.now(); const step = (t) => { const p = Math.min(1, (t - t0) / duration); el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))); if (p < 1) raf = requestAnimationFrame(step); }; raf = requestAnimationFrame(step); };
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting && !started) { started = true; run(); io.disconnect(); } }, { threshold: 0.4 });
    io.observe(el);
    return () => { io.disconnect(); cancelAnimationFrame(raf); };
  }, [target, duration]);
  return ref;
}
