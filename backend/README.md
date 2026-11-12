# BRUTALITY AI — Multi-Agent Accountability Backend

> **"Stop lying to yourself. Start delivering."**  
> An uncompromising, persistent multi-agent AI system that converts goals into measurable commitments, conducts daily check-ins, confronts excuses without insult, dynamically adapts schedules, and synthesizes weekly reality reports.

---

## 1. System Architecture

The BRUTALITY AI backend is built with **FastAPI**, **SQLAlchemy ORM (SQLite / PostgreSQL)**, and **Pydantic v2**.

### Multi-Agent Pipeline
1. **Onboarding Agent (`app/agents/onboarding_agent.py`)**
   - Breaks down ambitious goals into scheduled daily/weekly commitments with explicit completion criteria and reasonable daily workloads.
2. **Check-in Agent (`app/agents/checkin_agent.py`)**
   - Conducts personalized daily check-ins asking what was promised vs what was actually delivered today.
3. **Confront Agent (`app/agents/confront_agent.py`)**
   - Core accountability intelligence. Replaces old punishment/humiliation schemes. Detects avoidance patterns, vague rationalizations ("busy", "tired", "tomorrow"), and classifies execution status (`COMPLETED`, `PARTIALLY_COMPLETED`, `MISSED`, `BLOCKED`).
4. **Planner Agent (`app/agents/planner_agent.py`)**
   - Dynamically adapts future commitments forward when tasks are missed, without deleting completed achievements or overloading schedules.
5. **Reality Agent (`app/agents/reality_agent.py`)**
   - Calculates deterministic completion metrics from the database and generates weekly Reality Reports with brutal truth, excuse analysis, strengths, and actionable recalibration.
6. **Memory Agent (`app/agents/memory_agent.py`) & Service (`app/memory/`)**
   - Analyzes cross-session transcripts to distill behavioral tendencies, commitment styles, and recurring excuse triggers with complete multi-tenant user isolation.

### Central Orchestrator (`app/orchestrator/brutality_orchestrator.py`)
- Coordinates the entire agent lifecycle, manages database transactions, logs audit history, and enforces user isolation.

---

## 2. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health status |
| `POST` | `/api/auth/register` | Register new user account |
| `POST` | `/api/auth/login` | Authenticate and obtain JWT token |
| `GET` | `/api/auth/me` | Current authenticated user profile |
| `POST` | `/api/onboarding/start` | Agent 1: Goal breakdown & task generation |
| `GET` | `/api/goals` | List user goals |
| `POST` | `/api/goals` | Create goal |
| `GET` | `/api/goals/{id}` | Goal details with associated tasks |
| `PUT` | `/api/goals/{id}` | Update goal progress / status |
| `DELETE` | `/api/goals/{id}` | Delete goal |
| `GET` | `/api/tasks` | List commitments (filter by date/goal/status) |
| `POST` | `/api/tasks` | Create commitment |
| `PUT` | `/api/tasks/{id}` | Update commitment status |
| `DELETE` | `/api/tasks/{id}` | Delete commitment |
| `GET` | `/api/checkins/today` | Agent 2: Today's check-in questionnaire |
| `POST` | `/api/checkins/submit` | Agent 3 + Agent 4: Confront check-in & adapt plan |
| `GET` | `/api/checkins/history` | Historical check-in log |
| `GET` | `/api/reports/reality` | Agent 5: Latest weekly Reality Report |
| `POST` | `/api/reports/reality/generate` | Agent 5: Synthesize new Reality Report from DB stats |
| `GET` | `/api/reports/history` | List all historical reports |
| `GET` | `/api/dashboard/summary` | Consolidated dashboard feed & live stats |
| `GET` | `/api/dashboard/stats` | Raw deterministic performance metrics |
| `GET` | `/api/memory/insights` | Agent 6: Long-term behavioral insights |
| `POST` | `/api/chat/message` | Conversational coaching with memory context |

---

## 3. Quick Start & Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)

### Installation
```bash
cd backend
python -m pip install -r requirements.txt
```

### Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default configuration uses SQLite (`brutality_ai.db`) and `AI_PROVIDER=mock`, which allows full end-to-end functionality out of the box with zero external dependencies.

To use OpenAI:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
```

### Run the Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger API documentation: `http://localhost:8000/docs`

---

## 4. Running Automated Tests

Run the complete test suite with verbose output:
```bash
python -m pytest backend/tests -v
```
All 19 test cases verify:
- Individual agent reasoning & schema validation
- Complete REST API CRUD & filtering
- Full end-to-end multi-agent workflow
- Security, tenant data isolation, and edge-case resilience
