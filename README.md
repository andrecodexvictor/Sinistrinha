# Sinistrinha 🦍🎰

A modern, highly-scalable, and psychologically engaging slot machine simulation engineered with Django, FastAPI, React, and Django Channels. Built using a microservices architecture that separates transactional game logic from core probability modeling.

## Project Structure
*   **`/frontend`** (React/Vite) — SPA with Zustand state management, real-time WebSocket feeds, and Axios API integration.
*   **`/apps`** (Django) — User auth, payments, game orchestration, WebSockets, and database persistence.
*   **`/probability_engine`** (FastAPI) — Stateless probability calculation, target RTP enforcement, user profiling, and streak management.

## Features
*   **Full Frontend-Backend Integration:** Real JWT authentication, live spin API calls, and WebSocket-driven updates.
*   **Dynamic RTP (Return to Player):** The probability engine adjusts weights on-the-fly to hit targeted RTP metrics.
*   **Behavioral Modeling:** Profiles users to detect churn risks and adjust House Edge dynamically.
*   **Progressive Jackpot:** Shared prize pool synced via Redis and updated in real time via WebSockets.
*   **Leveling System:** 13-tier XP progression system that grants bonus coins, free spins, and virtual prizes.
*   **Observability Dashboard:** Custom Django admin panel displaying live metrics (Spins/h, RTP 24h/7d/30d, Active users, House Edge).
*   **CI/CD Pipeline:** GitHub Actions workflow for backend tests, frontend build, and Docker smoke tests.
*   **Full Containerization:** Single-command Docker Compose setup.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system diagram, API endpoint map, and data flow documentation.

## Getting Started

### Prerequisites
*   Docker & Docker Compose
*   Node.js 20+ (for frontend development)
*   Python 3.12+ (for backend development)
*   Supabase Account (for PostgreSQL DB)

### Quick Setup (Docker — Full Stack)
```bash
# 1. Copy and update your credentials
cp .env.example .env
# Edit .env with your Supabase credentials

# 2. Run the automated setup script
chmod +x setup.sh
./setup.sh
```

### Local Development (Frontend + Backend separately)

**Backend:**
```bash
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev   # Starts on http://localhost:3000 with API proxy to :8000
```

### Accessing the App
| Service                | URL                                   |
|------------------------|---------------------------------------|
| Frontend (dev)         | `http://localhost:3000`               |
| API Documentation      | `http://localhost:8000/api/docs/`     |
| Admin Dashboard        | `http://localhost:8000/admin/`        |
| Casino Dashboard       | `http://localhost:8000/admin/casino/dashboard/` |
| Probability Engine     | `http://localhost:8001/docs`          |
| Health Check           | `http://localhost:8000/health/`       |

### Default Accounts
| Role    | Username  | Password   | Balance  |
|---------|-----------|------------|----------|
| Admin   | `admin`   | `admin123` | R$10,000 |
| Player  | `player1` | `test1234` | R$100    |

## Running Tests

```bash
# Backend tests
docker-compose exec web pytest tests/ -v

# Frontend build check
cd frontend && npm run build
```

## CI/CD

The project uses **GitHub Actions** (`.github/workflows/ci.yml`) with the following jobs:

1. **Backend CI** — Installs deps, runs migrations, Django system check, pytest.
2. **Frontend CI** — Installs deps, TypeScript check, ESLint, production build.
3. **Probability Engine CI** — Validates imports and syntax.
4. **Docker Smoke Test** — Builds all containers, starts services, runs health checks (main branch only).

## Environment Variables

See [`.env.example`](.env.example) for the complete list with descriptions. Key variables:

| Variable               | Description                          |
|------------------------|--------------------------------------|
| `SUPABASE_DB_URL`      | PostgreSQL connection string         |
| `REDIS_URL`            | Redis connection string              |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins     |
| `VITE_API_URL`         | Backend URL for the frontend app     |
| `VITE_WS_URL`          | WebSocket URL for the frontend app   |

## License

Academic project — no real money involved.
