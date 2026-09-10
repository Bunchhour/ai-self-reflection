# 🧠 ReflectAI — AI-Powered Self-Reflection Platform

An intelligent self-reflection journaling platform that combines **adaptive entry modes**, **emotion tracking**, **cross-session pattern detection**, and **personalized micro-experiments** to help users build lasting self-awareness habits.

Built with a full-stack architecture: **Next.js 14** frontend, **FastAPI** backend, **LangGraph** agentic AI pipeline, **Groq** LLM inference, and **pgvector** semantic memory.

---

## ✨ Key Features

### 🎯 Adaptive Reflection Modes
- **⚡ Quick Pulse** (1–2 min) — Capture mood, energy, one thought, and a daily win
- **💬 Guided** (5–7 min) — AI selects the most relevant questions for you
- **📝 Deep Dive** (15+ min) — Full 12-category comprehensive reflection

### 🤖 Agentic AI Pipeline (LangGraph)
An 8-node agentic pipeline processes every reflection:

```
analyze_entry → analyze_emotions → retrieve_memories → detect_patterns
    → extract_interests → generate_reflection → suggest_experiment → save_memory
```

- **Smart Follow-up Questions** — AI detects superficial answers and asks deeper probing questions
- **Emotion Analysis** — Detects emotions the user may not have explicitly reported and identifies discrepancies
- **Semantic Memory** — pgvector cosine similarity search connects today's thoughts to historical reflections
- **Pattern Detection** — Identifies recurring emotional, behavioral, and time-usage patterns across sessions
- **Interest Extraction** — Automatically discovers emerging goals from recurring themes
- **Micro-Experiments** — Suggests daily actionable experiments with accept/modify/skip flow

### 🎨 Emotion Tracking
- **Plutchik Emotion Wheel** — Interactive emotion selector with 8 primary emotions and intensity levels
- **Mood Heatmap** — Calendar view of emotional patterns over time
- **Emotion Trends** — Line charts showing emotional shifts across days/weeks
- **Trigger Correlations** — AI-identified connections between events and emotions

### 🔥 Retention & Gamification
- **Streak Tracking** — Consecutive day counts with milestone celebrations
- **Streak Shields** — Earned at milestones (7, 14, 30, 60, 90 days); protect against missed days
- **Growth Score** — Composite metric based on consistency, depth, self-awareness, and experiments

### 🧪 Experiment Tracker
- AI-suggested daily experiments based on reflection patterns
- Accept, modify, or skip experiments
- Next-day check-in: Did you try it? How did it go?
- Effectiveness stats and category breakdown

### 🎯 Goal Emergence
- AI surfaces recurring interests from your reflections
- Interest nudges: "You've mentioned X multiple times. Track as a goal?"
- Manual goal creation with milestone tracking

### 🔒 Privacy & Data
- Full data export (JSON download)
- Account deletion with cascade
- Insight feedback mechanism (1–5 star rating)

---

## 🏗️ Architecture

```
┌──────────────────────────┐       ┌──────────────────────────┐
│     Next.js Frontend     │       │     FastAPI Backend       │
│  ┌────────────────────┐  │       │  ┌────────────────────┐  │
│  │   React + TailwindCSS  │ HTTP  │  │   Routers (7)       │  │
│  │   TanStack Query    │◄──────►│  │   auth, reflections  │  │
│  │   Radix UI          │       │  │   experiments, goals  │  │
│  │   Recharts          │       │  │   emotions, stats     │  │
│  └────────────────────┘  │       │  │   users              │  │
│  16 Pages + EmotionWheel │       │  └─────────┬────────────┘  │
└──────────────────────────┘       │            │               │
                                   │  ┌─────────▼────────────┐  │
                                   │  │ LangGraph Agent (8)   │  │
                                   │  │ ┌─analyze_entry      │  │
                                   │  │ ├─analyze_emotions   │  │
                                   │  │ ├─retrieve_memories  │  │
                                   │  │ ├─detect_patterns    │  │
                                   │  │ ├─extract_interests  │  │
                                   │  │ ├─generate_reflection│  │
                                   │  │ ├─suggest_experiment │  │
                                   │  │ └─save_memory        │  │
                                   │  └─────────┬────────────┘  │
                                   │            │               │
                                   │  ┌─────────▼────────────┐  │
                                   │  │ Services             │  │
                                   │  │ ├─auth_service       │  │
                                   │  │ ├─embedding_service  │  │
                                   │  │ ├─memory_service     │  │
                                   │  │ ├─stats_service      │  │
                                   │  │ └─experiment_service │  │
                                   │  └──────────────────────┘  │
                                   └────────────┬───────────────┘
                                                │
                                   ┌────────────▼───────────────┐
                                   │   PostgreSQL 16 + pgvector │
                                   │   7 tables, HNSW index     │
                                   │   384-dim vector embeddings│
                                   └────────────────────────────┘
                                                │
                                   ┌────────────▼───────────────┐
                                   │   External Services        │
                                   │   ├─ Groq API (LLM)       │
                                   │   └─ SentenceTransformers  │
                                   │      (all-MiniLM-L6-v2)   │
                                   └────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|:------|:-----------|
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, Radix UI, TanStack React Query, Recharts |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic |
| **Database** | PostgreSQL 16 with pgvector extension |
| **AI/LLM** | Groq API (`llama-3.3-70b-versatile`), LangGraph (state graph), SentenceTransformers (`all-MiniLM-L6-v2`) |
| **Auth** | JWT (python-jose) + bcrypt (passlib) |
| **Infra** | Docker, Docker Compose |

---

## 📁 Project Structure

```
ai-self-reflection/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── reflection_agent.py    # 8-node LangGraph pipeline
│   │   │   └── summary_agent.py       # Weekly/monthly AI summaries
│   │   ├── models/                    # 7 SQLAlchemy models
│   │   │   ├── user.py                # User + auth
│   │   │   ├── reflection.py          # DailyReflection + pgvector embedding
│   │   │   ├── experiment.py          # Micro-experiments
│   │   │   ├── emotion.py             # EmotionLog time-series
│   │   │   ├── goal.py                # Goal + InterestSignal
│   │   │   ├── stats.py               # UserStats (streaks, growth score)
│   │   │   └── feedback.py            # InsightFeedback
│   │   ├── routers/                   # 7 API routers
│   │   │   ├── auth.py                # register, login, me
│   │   │   ├── reflections.py         # CRUD + followup + weekly/monthly
│   │   │   ├── experiments.py         # respond, review, stats
│   │   │   ├── emotions.py            # trends, heatmap, triggers
│   │   │   ├── goals.py               # CRUD + interest signals
│   │   │   ├── stats.py               # streaks, growth score, achievements
│   │   │   └── users.py               # export, delete account, feedback
│   │   ├── schemas/                   # Pydantic request/response models
│   │   ├── services/                  # Business logic services
│   │   │   ├── auth_service.py        # JWT + bcrypt
│   │   │   ├── embedding_service.py   # Async SentenceTransformers
│   │   │   ├── memory_service.py      # pgvector cosine similarity
│   │   │   ├── stats_service.py       # Streak + shield logic
│   │   │   └── experiment_service.py
│   │   ├── config.py                  # Pydantic Settings
│   │   ├── database.py                # Async SQLAlchemy engine
│   │   └── main.py                    # FastAPI app
│   ├── alembic/                       # Database migrations
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx               # Landing page
│   │   │   ├── (auth)/                # Login & Register
│   │   │   └── (app)/                 # Protected routes
│   │   │       ├── dashboard/         # Home dashboard
│   │   │       ├── reflect/           # Entry mode selector
│   │   │       │   ├── quick/         # Quick Pulse form
│   │   │       │   ├── guided/        # Guided conversation
│   │   │       │   ├── deep/          # Full 12-category form
│   │   │       │   ├── followup/      # AI follow-up questions
│   │   │       │   └── result/        # AI insights display
│   │   │       ├── history/           # List + detail + weekly + monthly
│   │   │       ├── emotions/          # Mood heatmap & trends
│   │   │       ├── experiments/       # Experiment tracker
│   │   │       ├── goals/             # Goal management
│   │   │       └── settings/          # Privacy & data export
│   │   ├── components/
│   │   │   ├── emotions/EmotionWheel.tsx  # Plutchik wheel selector
│   │   │   ├── layout/               # Header, Sidebar, ProtectedRoute
│   │   │   ├── providers/             # Auth & Query providers
│   │   │   └── ui/                    # 11 Radix UI primitives
│   │   └── lib/
│   │       ├── api.ts                 # Centralized API client
│   │       └── utils.ts               # cn() helper
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A [Groq API key](https://console.groq.com/keys) (free tier available)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-self-reflection.git
cd ai-self-reflection
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/self_reflection

# Auth
SECRET_KEY=your-secret-key-change-in-production-use-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Groq AI
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start with Docker Compose

```bash
docker compose up --build
```

This starts 3 services:

| Service | URL | Description |
|:--------|:----|:------------|
| **Frontend** | [http://localhost:3000](http://localhost:3000) | Next.js web application |
| **Backend** | [http://localhost:8000](http://localhost:8000) | FastAPI REST API |
| **Database** | `localhost:5432` | PostgreSQL 16 + pgvector |

### 4. Run Database Migrations

In a separate terminal:

```bash
docker exec -it self_reflection_backend alembic upgrade head
```

### 5. Open the App

Navigate to [http://localhost:3000](http://localhost:3000), register an account, and start your first reflection!

---

## 🖥️ Local Development (Without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .

# Start PostgreSQL with pgvector locally, then:
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 📡 API Endpoints

### Auth (`/api/auth`)
| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Login and receive JWT token |
| `GET` | `/api/auth/me` | Get current authenticated user |

### Reflections (`/api/reflections`)
| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `POST` | `/api/reflections/` | Create daily reflection (with entry mode) |
| `GET` | `/api/reflections/` | List reflections (paginated) |
| `GET` | `/api/reflections/today` | Get today's reflection |
| `GET` | `/api/reflections/{id}` | Get reflection by ID |
| `DELETE` | `/api/reflections/today` | Delete today's reflection |
| `DELETE` | `/api/reflections/{id}` | Delete a reflection |
| `POST` | `/api/reflections/{id}/followup` | Submit follow-up answers |
| `GET` | `/api/reflections/weekly` | AI-generated weekly summary |
| `GET` | `/api/reflections/monthly` | AI-generated monthly summary |

### Experiments (`/api/experiments`)
| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `GET` | `/api/experiments/` | List experiments |
| `GET` | `/api/experiments/pending` | Get pending experiment |
| `POST` | `/api/experiments/{id}/respond` | Accept/modify/skip |
| `POST` | `/api/experiments/{id}/review` | Submit rating & feedback |
| `GET` | `/api/experiments/stats` | Effectiveness statistics |

### Emotions (`/api/emotions`)
| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `GET` | `/api/emotions/trends` | Emotion trends (7d/30d/90d) |
| `GET` | `/api/emotions/heatmap` | Calendar heatmap data |
| `GET` | `/api/emotions/triggers` | AI trigger correlations |

### Goals (`/api/goals`)
| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `GET` | `/api/goals/` | List goals |
| `POST` | `/api/goals/` | Create a goal |
| `PATCH` | `/api/goals/{id}` | Update goal status |
| `GET` | `/api/goals/interests` | Surfaced interest signals |
| `POST` | `/api/goals/interests/{id}/respond` | Respond to interest nudge |

### Stats (`/api/stats`)
| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `GET` | `/api/stats/` | Streaks, growth score, achievements |
| `GET` | `/api/stats/achievements` | All achievements |

### User (`/api/user`)
| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `GET` | `/api/user/export` | Export all user data (JSON) |
| `DELETE` | `/api/user/account` | Delete account |
| `POST` | `/api/user/feedback` | Submit insight feedback |

Full API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI).

---

## 🧪 Database Schema

7 tables with pgvector extension:

| Table | Purpose |
|:------|:--------|
| `users` | User accounts and authentication |
| `reflections` | Daily reflections with 384-dim vector embeddings (HNSW index) |
| `experiments` | AI-suggested micro-experiments with tracking |
| `emotion_logs` | Time-series emotion data (user-reported + AI-detected) |
| `user_stats` | Streaks, growth scores, streak shields, achievements |
| `interest_signals` | AI-extracted recurring themes/topics |
| `goals` | User goals (emerged from interests or manually created) |
| `insight_feedback` | User ratings on AI-generated insights |

---

## 🔐 Security

- Passwords hashed with **bcrypt** (minimum 8 characters enforced)
- Authentication via **JWT tokens** (24-hour expiry)
- CORS restricted to frontend origin
- Database-level cascade deletion for account removal
- `.env` excluded from version control via `.gitignore`
- Connection pool health checks (`pool_pre_ping`) for database reliability

---

## 📊 AI Pipeline Details

Each reflection is processed by an **8-node LangGraph state graph**:

1. **`analyze_entry`** — Determines if follow-up questions are needed based on entry mode and answer depth
2. **`analyze_emotions`** — Extracts emotions from text, compares with user-reported emotions, identifies discrepancies
3. **`retrieve_memories`** — Generates 384-d embedding, queries pgvector for top 5 similar past reflections
4. **`detect_patterns`** — Cross-references today's entry with historical data to spot recurring patterns
5. **`extract_interests`** — Identifies emerging topics and categorizes by domain (Career, Health, Learning, etc.)
6. **`generate_reflection`** — Produces structured AI insights (summary, highlights, difficulties, learnings, observations)
7. **`suggest_experiment`** — Proposes a small actionable experiment for the next day
8. **`save_memory`** — Persists all AI outputs, embeddings, experiments, and emotion logs to the database

The pipeline uses **Groq API** with `llama-3.3-70b-versatile` for fast inference and **JSON mode** for structured outputs with automatic retry and fallback parsing.

---

## 🗺️ User Flow

```
Register → Login → Dashboard
                      │
                      ▼
            ┌─── Entry Mode Selector ───┐
            │         │                 │
          Quick     Guided           Deep Dive
          Pulse     (3–5 Qs)         (12 cats)
            │         │                 │
            └─────────┼─────────────────┘
                      ▼
              AI Follow-up Questions
              (if needed)
                      │
                      ▼
              AI Insights & Results
              ├─ Daily Synthesis
              ├─ Patterns Detected
              ├─ Emotion Analysis
              └─ Suggested Experiment
                  (Accept / Skip)
                      │
                      ▼
              ┌───────┼───────┐
              │       │       │
          History  Weekly  Monthly
           List   Summary  Review
              │       │       │
              └───────┼───────┘
                      │
              ┌───────┼───────┐
              │       │       │
          Emotions Experiments Goals
          Dashboard  Tracker   Page
```

---

## ⚠️ Disclaimer

This platform is a **self-reflection and personal growth tool**, not a substitute for professional therapy or mental health treatment. If you are experiencing mental health difficulties, please consult a qualified professional.

---

## 📄 License

This project is for educational purposes.

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) — Ultra-fast LLM inference
- [LangGraph](https://github.com/langchain-ai/langgraph) — Stateful AI agent framework
- [pgvector](https://github.com/pgvector/pgvector) — Vector similarity search for PostgreSQL
- [SentenceTransformers](https://www.sbert.net/) — State-of-the-art text embeddings
- [Plutchik's Wheel of Emotions](https://en.wikipedia.org/wiki/Robert_Plutchik) — Emotion model inspiration
