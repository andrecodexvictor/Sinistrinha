# Sinistrinha Game Architecture 🦍

The Sinistrinha system is built on a microservices-inspired architecture designed for high scalability, realtime synchronization, and complex probability modeling. The system is split into three main tiers:

## 1. Frontend (React + TypeScript)
_Target implementation: Agent 3_
* Handles user interface, animations, sound effects, and WebSocket connections.
* Built using Vite for fast bundling.

## 2. Game Engine Core (Django + Channels)
_Implemented by: Agent 1 (Base Auth/Payments) + Agent 4 (Game Logic + Orchestration)_
This is the central state manager and orchestrator. It handles everything that must be strictly transactional.

*   **REST API:**
    *   Auth, Payments (Deposits/Withdrawals).
    *   `/api/game/spin/`: The main orchestrator endpoint. It validates the user's bet, debits their balance, calls the Probability Engine, pays out their winnings, checks for jackpots and free spins, awards XP, handles level-ups, saves exactly what happened, and finally triggers WebSocket notifications.
*   **WebSockets (Django Channels + Redis):**
    *   Pushes real-time updates to users (balance changes, level-ups) and global events (big wins broadcast to the entire site).
*   **Systems:**
    *   **JackpotSystem:** Progressive shared pool funded by 2% of every bet. Uses row-level locks on the DB and caches the value in Redis for extremely fast reads.
    *   **LevelSystem:** 13-tier configuration granting XP multipliers for high bets/events, and paying out free spins and coins upon leveling up.
    *   **FreeSpinSystem:** Manages free spin lifecycle with 24-hour expiry and usage tracking.
*   **Observability:** Custom Django Admin dashboard at `/admin/casino/dashboard/` showing calculated RTPs, house edges, live charts, active users, and the live jackpot pool.

## 3. Probability Engine (FastAPI)
_Implemented by: Agent 2_
A standalone, high-performance, stateless microservice dedicated to RNG, statistical modeling, and player psychology.

*   **Logic Components:**
    *   **WeightEngine:** Virtual reel mapping, adjusting probabilities dynamically per reel.
    *   **HouseEdgeController:** Manipulates reel weights to enforce a targeted RTP (e.g., 87%), forcing "near misses" and detecting winning/losing streaks to ride out volatility.
    *   **AdaptiveLearningAgent:** Profiles player behavior (e.g., "whale", "churn_risk") using EWMA (Exponential Weighted Moving Average) and recommends whether the House Edge should go easy on them to keep them playing or tighten up.
    *   **PayoutCalculator:** Evaluates the reels for line wins, scatter bonuses, and computes exactly how much XP to give.

## Architecture Flow (A Single Spin)
1.  **Frontend** sends `POST /api/game/spin/` with `bet_amount`.
2.  **Django** validates balance, rate-limits (max 60/min), and debits the bet.
3.  **Django** sends an HTTP request to **FastAPI** `POST /probability/spin` detailing the user ID, level, bet, and remaining budget.
4.  **FastAPI** calculates the outcome:
    *   _LearningAgent_ assesses player's churn risk.
    *   _HouseEdgeController_ applies modifiers based on target RTP and churn risk.
    *   _WeightEngine_ generates the reels.
    *   _PayoutCalculator_ analyzes the win.
5.  **FastAPI** returns the result to **Django**.
6.  **Django** checks for jackpot overrides, applies level progress, saves the `SpinHistory`, and updates the user's balance.
7.  **Django Channels** broadcasts the new balance directly to the user, and if it's a "big win", broadcasts it to the public casino feed.
8.  **Frontend** renders the spin.

## Infrastructure Setup
*   **Docker Compose:** Fully containerized setup containing Web (Django), Celery, Celery Beat, Redis, Probability Engine (FastAPI), and an Nginx reverse proxy.
*   **Database:** Supabase PostgreSQL setup with Prisma connection pooling recommended.
*   **Setup:** A `setup.sh` script installs dependencies, seeds superusers, and configures the Leveling map and Jackpot pool out-of-the-box.
