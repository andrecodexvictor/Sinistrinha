# Sinistrinha 🦍🎰

A modern, highly-scalable, and psychologically engaging slot machine simulation engineered with Django, FastAPI, React, and Django Channels. Built using a microservices architecture that separates transactional game logic from core probability modeling.

## Project Structure
*   **/backend** (Django) — User auth, payments, game orchestration, WebSockets, and database persistence.
*   **/probability_engine** (FastAPI) — Stateless probability calculation, target RTP enforcement, user profiling, and streak management.
*   **/frontend** (React/Vite) — *To be implemented.*

## Features
*   **Dynamic RTP (Return to Player):** The probability engine adjusts weights on-the-fly to hit targeted RTP metrics and maximize user engagement.
*   **Behavioral Modeling:** Profiles users to detect churn risks and adjust House Edge dynamically.
*   **Progressive Jackpot:** Shared prize pool synced via Redis and updated in real time via WebSockets.
*   **Leveling System:** 13-tier XP progression system that grants bonus coins, free spins, and virtual prizes.
*   **Observability Dashboard:** Custom Django admin panel displaying live metrics (Spins/h, RTP 24h/7d/30d, Active users, House Edge).
*   **Full Containerization:** Single-command Docker Compose setup.

## Getting Started

Check the complete technical overview in `ARCHITECTURE.md`.

### Prerequisites
*   Docker & Docker Compose
*   Supabase Account (for PostgreSQL DB)

### Quick Setup
We provide an automated setup script that builds containers, runs migrations, seeds levels, initializes the jackpot pool, and creates sample accounts:

```bash
# 1. Update your .env credentials
cp .env.example .env

# 2. Run the quickstart script
chmod +x setup.sh
./setup.sh
```

### Accessing the App
After running `setup.sh`:
*   📍 **API Docs:** `http://localhost:8000/api/docs/`
*   📍 **Admin Dashboard:** `http://localhost:8000/admin/casino/dashboard/`
*   📍 **Probability API Docs:** `http://localhost:8001/docs`

**Default Accounts:**
*   Admin: `admin` / `admin123`
*   Player: `player1` / `test1234` (Starts with R$100.00)

## Running Tests
Run the integration test suite (Django + Probability Engine integration) via pytest:
```bash
docker-compose exec web pytest tests/ -v
```
