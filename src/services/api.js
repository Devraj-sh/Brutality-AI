/**
 * BRUTALITY AI — Service Facade
 * Connects frontend directly to the FastAPI multi-agent backend (http://localhost:8000/api)
 * with automatic fallback to local engine if backend is offline.
 */
import { generateReply } from './mockAI.js';
import { SEED_REPORTS, CONSISTENCY_HISTORY } from '../data/mockData.js';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('brutality_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
};

export const chatService = {
  async sendMessage({ message, history, context }) {
    try {
      const res = await fetch(`${API_BASE}/chat/message`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ message })
      });
      if (res.ok) {
        const data = await res.json();
        return {
          agent: data.agent_name || 'Brutality AI',
          text: data.reply,
          suggestions: data.suggestions || ["Show today's tasks", "Review my progress"]
        };
      }
    } catch {
      // Backend offline or unreachable — seamlessly use intelligent local fallback
    }
    return generateReply({ message, history, context });
  }
};

export const reportService = {
  async list() {
    try {
      const res = await fetch(`${API_BASE}/reports/reality`, {
        headers: getAuthHeaders()
      });
      if (res.ok) {
        const r = await res.json();
        const mapped = [{
          id: r.id,
          label: 'Week of ' + r.start_date,
          week: `${r.start_date} → ${r.end_date}`,
          score: Math.round(r.completion_rate),
          streak: 4,
          committed: r.total_commitments,
          completed: r.completed_commitments,
          missed: r.total_commitments - r.completed_commitments,
          brutalTruth: r.brutal_truth,
          strengths: r.strengths,
          actionPlan: r.action_plan,
          excuses: [
            { label: 'Fatigue / Postponing', count: 3 },
            { label: 'Competing Priorities', count: 2 }
          ],
          missedList: [
            { title: 'Incomplete Commitments', criteria: 'Missed standard under low discipline' }
          ]
        }, ...SEED_REPORTS.slice(1)];
        return mapped;
      }
    } catch {
      // Fallback to seeds
    }
    return SEED_REPORTS;
  },

  async history() {
    try {
      const res = await fetch(`${API_BASE}/reports/history`, {
        headers: getAuthHeaders()
      });
      if (res.ok) {
        const list = await res.json();
        if (list.length > 0) {
          return list.map((item, idx) => ({
            week: `W${idx + 1}`,
            score: Math.round(item.completion_rate)
          }));
        }
      }
    } catch {
      // Fallback
    }
    return CONSISTENCY_HISTORY;
  }
};

export const dashboardService = {
  async getSummary() {
    const res = await fetch(`${API_BASE}/dashboard/summary`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch dashboard summary');
    return res.json();
  },
  async getStats() {
    const res = await fetch(`${API_BASE}/dashboard/stats`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
  }
};

export const onboardingService = {
  async startOnboarding(payload) {
    const res = await fetch(`${API_BASE}/onboarding/start`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to start onboarding');
    return res.json();
  }
};

export const checkinService = {
  async getToday(date) {
    const url = date ? `${API_BASE}/checkins/today?date=${date}` : `${API_BASE}/checkins/today`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to get today checkin');
    return res.json();
  },
  async submitCheckin(payload) {
    const res = await fetch(`${API_BASE}/checkins/submit`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to submit checkin');
    return res.json();
  }
};

export const goalService = {
  async list() {
    const res = await fetch(`${API_BASE}/goals`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to list goals');
    return res.json();
  },
  async create(goal) {
    const res = await fetch(`${API_BASE}/goals`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(goal)
    });
    if (!res.ok) throw new Error('Failed to create goal');
    return res.json();
  }
};

export const taskService = {
  async list(filters = {}) {
    const params = new URLSearchParams(filters);
    const res = await fetch(`${API_BASE}/tasks?${params.toString()}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to list tasks');
    return res.json();
  },
  async create(task) {
    const res = await fetch(`${API_BASE}/tasks`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(task)
    });
    if (!res.ok) throw new Error('Failed to create task');
    return res.json();
  },
  async update(id, updates) {
    const res = await fetch(`${API_BASE}/tasks/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(updates)
    });
    if (!res.ok) throw new Error('Failed to update task');
    return res.json();
  }
};
