/** Safe localStorage wrapper. Demo persistence only — swap for API calls later. */
const PREFIX = 'brutalityai:v1:';
export const storage = {
  get(key, fallback) {
    try { const raw = localStorage.getItem(PREFIX + key); return raw ? JSON.parse(raw) : fallback; }
    catch { return fallback; }
  },
  set(key, value) {
    try { localStorage.setItem(PREFIX + key, JSON.stringify(value)); } catch { /* storage unavailable */ }
  },
  remove(key) {
    try { localStorage.removeItem(PREFIX + key); } catch { /* noop */ }
  },
};
