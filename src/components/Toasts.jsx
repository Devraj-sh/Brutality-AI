import { CheckCircle2, AlertTriangle } from 'lucide-react';
import { useApp } from '../context/AppStore.jsx';
export default function Toasts() {
  const { toasts } = useApp();
  return (
    <div className="toast-stack" aria-live="polite">
      {toasts.map((t) => (
        <div key={t.id} className={`toast ${t.type === 'error' ? 'error' : ''}`}>
          {t.type === 'error' ? <AlertTriangle size={18} color="#f84848" /> : <CheckCircle2 size={18} color="#D6FF3D" />}{t.message}
        </div>
      ))}
    </div>
  );
}
