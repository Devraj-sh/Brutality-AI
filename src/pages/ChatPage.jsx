import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Send, Paperclip, Mic, RotateCcw, X } from 'lucide-react';
import AppShell from '../components/AppShell.jsx';
import ChatBubble, { TypingIndicator } from '../components/ChatBubble.jsx';
import Button from '../components/Button.jsx';
import { useApp } from '../context/AppStore.jsx';
import { chatService } from '../services/api.js';
import { detectIntent } from '../services/mockAI.js';
import { storage } from '../services/storage.js';
import { WELCOME_MESSAGE, GOAL_CHIPS, QUICK_ACTIONS } from '../data/mockData.js';

const clock = () => new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
const uid = () => Math.random().toString(36).slice(2, 10);
const welcome = () => [{ id: uid(), role: 'ai', agent: 'Onboarding Agent', text: WELCOME_MESSAGE, time: clock() }];

const QUICK_PROMPT = { progress: 'Review my progress', tasks: "Show today's tasks", excuses: 'Analyse my excuses', report: 'Generate reality report' };

export default function ChatPage() {
  const { tasks, stats, saveGoal, toast } = useApp();
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState(() => storage.get('chat', null) || welcome());
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const [attachment, setAttachment] = useState(null);
  const [listening, setListening] = useState(false);
  const scroller = useRef(null);
  const area = useRef(null);
  const fileRef = useRef(null);
  const recog = useRef(null);
  const alive = useRef(true);

  useEffect(() => { alive.current = true; return () => { alive.current = false; recog.current?.stop?.(); }; }, []);
  useEffect(() => storage.set('chat', messages.slice(-80)), [messages]);
  useEffect(() => { scroller.current?.scrollTo({ top: scroller.current.scrollHeight, behavior: 'smooth' }); }, [messages, typing]);
  useEffect(() => { // auto-grow
    const a = area.current; if (!a) return; a.style.height = 'auto'; a.style.height = Math.min(a.scrollHeight, 160) + 'px';
  }, [input]);

  const newConversation = useCallback(() => { setMessages(welcome()); setInput(''); setAttachment(null); setTyping(false); storage.remove('chat'); }, []);
  useEffect(() => { if (params.get('new')) { newConversation(); setParams({}, { replace: true }); } }, [params, newConversation, setParams]);

  const send = useCallback(async (raw) => {
    const text = (raw ?? input).trim();
    if ((!text && !attachment) || typing) return;
    const userMsg = { id: uid(), role: 'user', text: text || `Sent a file: ${attachment}`, time: clock(), attachment };
    const history = [...messages, userMsg];
    setMessages(history); setInput(''); setAttachment(null); setTyping(true);
    try {
      // >>> Swap chatService.sendMessage for a real API call when the backend exists.
      const reply = await chatService.sendMessage({ message: text || 'file', history, context: { tasks, stats } });
      if (!alive.current) return;
      setMessages((m) => [...m, { id: uid(), role: 'ai', time: clock(), ...reply }]);
    } catch {
      toast('The AI did not respond. Try again.', 'error');
    } finally { if (alive.current) setTyping(false); }
  }, [input, attachment, typing, messages, tasks, stats, toast]);

  const addGoalFromChat = () => {
    const goalMsg = [...messages].reverse().find((m) => m.role === 'user' && detectIntent(m.text).startsWith('goal'));
    const details = [...messages].reverse().find((m) => m.role === 'user' && m !== goalMsg);
    const title = (goalMsg?.text || 'New goal').replace(/[.!]+$/, '').slice(0, 70);
    saveGoal({ title: title.charAt(0).toUpperCase() + title.slice(1), description: 'Created from a conversation with Brutality AI.', priority: 'medium',
      targetDate: new Date(Date.now() + 56 * 864e5).toISOString().slice(0, 10), commitments: [details?.text && details.text.length < 70 ? `Daily: ${details.text}` : 'Work on this goal for 45 minutes'] });
    navigate('/goals');
  };

  const onKey = (e) => { if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); send(); } };

  const voice = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { toast('Voice input is not supported in this browser.', 'error'); return; }
    if (listening) { recog.current?.stop(); return; }
    const r = new SR(); r.lang = 'en-IN'; r.interimResults = false;
    r.onresult = (e) => setInput((v) => (v ? v + ' ' : '') + e.results[0][0].transcript);
    r.onend = () => setListening(false); r.onerror = () => { setListening(false); toast('Could not access the microphone.', 'error'); };
    recog.current = r; setListening(true); try { r.start(); } catch { setListening(false); }
  };

  const hasUser = messages.some((m) => m.role === 'user');
  const lastAI = [...messages].reverse().find((m) => m.role === 'ai');

  return (
    <AppShell
      title={<div className="chat-title"><b>Brutality AI</b><span><i className="online" />AI Accountability Agent · Online (demo)</span></div>}
      actions={<Button variant="w" size="sm" onClick={newConversation}><RotateCcw size={15} /> <span className="hide-sm">Clear chat</span></Button>}
    >
      <div className="chat-area">
        <div className="chat-scroll" ref={scroller} role="log" aria-live="polite" aria-label="Conversation">
          <div className="chat-inner">
            {messages.map((m) => <ChatBubble key={m.id} msg={m} onAddGoal={addGoalFromChat} />)}
            {!hasUser && (
              <div className="chip-row" aria-label="Suggested goals">
                {GOAL_CHIPS.map((c) => <button key={c} className="pill" onClick={() => send(c)}>{c}</button>)}
              </div>
            )}
            {typing && <TypingIndicator />}
            {!typing && hasUser && lastAI?.suggestions?.length > 0 && (
              <div className="chip-row">{lastAI.suggestions.map((s) => <button key={s} className="pill sm" onClick={() => send(s)}>{s}</button>)}</div>
            )}
          </div>
        </div>

        <div className="composer">
          <div className="composer-inner">
            <div className="quick-row">
              {QUICK_ACTIONS.map((q) => <button key={q.id} className="pill sm" onClick={() => send(QUICK_PROMPT[q.id])} disabled={typing}>{q.label}</button>)}
            </div>
            {attachment && <div className="attach-chip pending">{attachment}<button onClick={() => setAttachment(null)} aria-label="Remove attachment"><X size={13} /></button></div>}
            <div className="input-row">
              <input ref={fileRef} type="file" hidden onChange={(e) => { const f = e.target.files?.[0]; if (f) { setAttachment(f.name); toast(`Attached ${f.name} (kept in this browser only)`); } e.target.value = ''; }} />
              <button className="tool-btn" onClick={() => fileRef.current?.click()} aria-label="Attach a file"><Paperclip size={20} /></button>
              <textarea ref={area} rows={1} value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={onKey} placeholder="Tell me what you did. Or didn't." aria-label="Message Brutality AI" />
              <button className={`tool-btn ${listening ? 'live' : ''}`} onClick={voice} aria-label={listening ? 'Stop voice input' : 'Start voice input'} aria-pressed={listening}><Mic size={20} /></button>
              <Button variant="blue" icon onClick={() => send()} disabled={typing || (!input.trim() && !attachment)} aria-label="Send message"><Send size={19} /></Button>
            </div>
            <div className="hint">Enter to send · Shift + Enter for a new line</div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
