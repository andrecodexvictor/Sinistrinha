# Sinistrinha — Integration Documentation

## Overview

This document covers the Supabase integration, leveling/bonus system, and real-time WebSocket communication for the Sinistrinha game.

---

## 1. Supabase Configuration

### Environment Variables

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL (e.g., `https://xxx.supabase.co`) |
| `SUPABASE_KEY` | Anon (public) key for client-side operations |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key for server-side operations (bypasses RLS) |
| `SUPABASE_DB_URL` | PostgreSQL connection string via Supabase pooler |

### Row Level Security (RLS)

RLS policies are defined in `apps/game/migrations/sql/0002_rls_policies.sql`. Execute this SQL in the **Supabase Dashboard → SQL Editor** after running Django migrations.

| Table | Policy |
|---|---|
| `users_userprofile` | Users read/update own profile only |
| `game_spinhistory` | Users read own spins; inserts via service_role |
| `game_levelconfig` | Read-only for all authenticated users |
| `game_jackpotpool` | Read-only for all authenticated users |
| `payments_transaction` | Users read own transactions only |

### Supabase Client Module

`apps/integrations/supabase_client.py` provides:
- `get_client()` — cached Supabase client singleton
- `broadcast_realtime(channel, event, payload)` — optional Supabase Realtime broadcasting

---

## 2. Leveling & Bonus System

### XP Progression

Every spin awards XP based on the outcome:

| Outcome | XP |
|---|---|
| Any spin | +10 XP |
| Winning spin | +25 XP bonus |
| Jackpot | +500 XP bonus |

### Level Tiers

| Level | XP Required | Bonus Coins | Free Spins | Prize |
|---|---|---|---|---|
| 1 | 0 | 0 | 0 | Newbie (Estagiário) |
| 2 | 500 | 50 | 3 | Pendrive 8GB |
| 3 | 1,500 | 150 | 5 | Teclado Mecânico |
| 4 | 3,500 | 350 | 7 | Mouse Gamer |
| 5 | 7,000 | 700 | 10 | RAM DDR5 16GB |
| 6 | 12,000 | 1,200 | 12 | SSD NVMe 1TB |
| 7 | 20,000 | 2,000 | 15 | Monitor 144Hz |
| 8 | 35,000 | 3,500 | 20 | CPU Ryzen 7 |
| 9 | 60,000 | 6,000 | 25 | GPU RTX 4070 |
| 10 | 100,000 | 10,000 | 50 | Gorila Dourado (Setup Completo) |

Seed levels with: `python manage.py seed_levels`

### RTP by Level

Higher levels grant slightly more generous RTP:

| Level | RTP |
|---|---|
| 1 | 85.0% |
| 5 | 87.0% |
| 10 | 89.5% |

### Services

- **LevelService** (`apps/game/services/level_service.py`): `award_xp()`, `check_level_up()`, `get_current_rtp()`, `get_rtp_modifier()`
- **BonusService** (`apps/game/services/bonus_service.py`): `grant_free_spins()`, `consume_free_spin()`, `grant_bonus_coins()`, `apply_level_bonus()`

---

## 3. Real-time WebSocket Communication

### Channels

| Endpoint | Group | Auth | Purpose |
|---|---|---|---|
| `ws://host/ws/casino/` | `casino_live` | None | Public feed: jackpot, recent wins |
| `ws://host/ws/player/<id>/` | `player_{id}` | JWT (query string) | Private: balance, level-up, bonuses |

### Public Events (`casino_live`)

```json
// jackpot_update
{"type": "jackpot_update", "data": {"jackpot_amount": 5000.00}}

// recent_win
{"type": "recent_win", "data": {"username": "player1", "amount": 500.0, "symbol": "🎮", "is_jackpot": false}}
```

### Private Events (`player_{id}`)

```json
// balance_update
{"type": "balance_update", "data": {"balance": 1500.00}}

// level_up
{"type": "level_up", "data": {"old_level": 2, "new_level": 3, "bonus_coins": 150.0, "free_spins": 5, "prize_name": "Teclado Mecânico"}}

// free_spins_update
{"type": "free_spins_update", "data": {"free_spins": 8}}
```

### Connecting to Personal Channel

```javascript
const ws = new WebSocket(`ws://host/ws/player/${userId}/?token=${jwtAccessToken}`);
```

### Periodic Tasks (Celery Beat)

| Task | Interval |
|---|---|
| `broadcast_jackpot_ticker` | Every 5 seconds |
| `snapshot_jackpot` | Every hour |
| `process_pending_withdrawals` | Every 15 minutes |

---

## 4. Spin API Response

`POST /api/game/spin/`

**Request:**
```json
{"bet_amount": "10.00", "use_free_spin": false}
```

**Response:**
```json
{
  "spin_id": 42,
  "reels": ["ram", "ram", "ram", "mouse", "teclado"],
  "payout": 20.0,
  "combination_type": "3x ram",
  "is_jackpot": false,
  "multiplier": 2.0,
  "free_spins_awarded": 0,
  "xp_earned": 35,
  "new_balance": 1010.00,
  "new_level": 1,
  "new_xp": 235,
  "free_spins_remaining": 0,
  "bonuses": [],
  "winning_symbol": "ram",
  "wild_used": false
}
```
