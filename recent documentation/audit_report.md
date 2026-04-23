# 🦍 Sinistrinha — Full Repository Audit

> **Date:** 2026-04-23 · **Scope:** Full codebase (Django backend, FastAPI microservice, React frontend, Docker, Nginx, Vercel)

---

## Table of Contents

1. [Port Matrix & Networking](#1-port-matrix--networking)
2. [Prioritized Findings (Critical → Low)](#2-prioritized-findings)
3. [Security Hardening Profile](#3-security-hardening-profile)
4. [Test Gap Analysis & Top-10 Tests](#4-test-gap-analysis)
5. [GitHub Issue Backlog](#5-github-issue-backlog)
6. [7-Day Remediation Plan](#6-7-day-remediation-plan)

---

## 1. Port Matrix & Networking

### Source-of-Truth Port Matrix

| Service | Internal Port | Exposed Port | Bind Address | Config Source |
|---|---|---|---|---|
| **Django (Daphne)** | 8000 | 8000 | `0.0.0.0` | [docker-compose.yml:6](file:///c:/Users/adm/Desktop/Sinistrinha/docker-compose.yml#L6) |
| **Probability Engine (Uvicorn)** | 8001 | 8001 | `0.0.0.0` | [docker-compose.yml:24](file:///c:/Users/adm/Desktop/Sinistrinha/docker-compose.yml#L24) |
| **Redis** | 6379 | 6379 | default | [docker-compose.yml:35](file:///c:/Users/adm/Desktop/Sinistrinha/docker-compose.yml#L35) |
| **Nginx** | 80 | 80 | — | [docker-compose.yml:65](file:///c:/Users/adm/Desktop/Sinistrinha/docker-compose.yml#L65) |
| **Frontend (Vite dev)** | 3000 | — (not in compose) | — | [vite.config.ts:7](file:///c:/Users/adm/Desktop/Sinistrinha/frontend/vite.config.ts#L7) |
| **Celery Worker** | — | — | — | [docker-compose.yml:41](file:///c:/Users/adm/Desktop/Sinistrinha/docker-compose.yml#L41) |
| **Celery Beat** | — | — | — | [docker-compose.yml:52](file:///c:/Users/adm/Desktop/Sinistrinha/docker-compose.yml#L52) |

### Networking Misconfigurations

| # | Issue | Symptom | Fix |
|---|---|---|---|
| N1 | `.env` uses `REDIS_URL=redis://localhost:6379/1` but Docker needs `redis://redis:6379/1` | Web/Celery containers can't connect to Redis | `.env.example` is correct (`redis://redis:6379/1`). Fix `.env` to match, or add `REDIS_URL` override in `docker-compose.yml` `environment:` blocks. |
| N2 | Vite dev server port is `3000` but `.env.example` lists `CORS_ALLOWED_ORIGINS` as both `3000` and `5173` | Works, but stale origin `5173` is vestigial | Remove `5173` from CORS list or update Vite port to `5173`. |
| N3 | Nginx `location /` proxies **everything** to Django; no static frontend hosting | Frontend can never be served through Nginx | Add a `location /` block serving `frontend/dist/` with fallback to `index.html`, move API proxy under `/api/`. |
| N4 | Probability engine ports `8001:8001` exposed to host — unnecessary when Nginx proxies it | Security surface: direct access bypasses any auth layer | Remove `ports:` from `probability_engine` service; keep only `expose: [8001]`. |
| N5 | Frontend has `socket.io-client` dep but backend uses Django Channels (native WS) | `socket.io` and raw WebSocket are **incompatible protocols** | Replace `socket.io-client` with native `WebSocket` API or a thin wrapper. |

---

## 2. Prioritized Findings

### 🔴 CRITICAL

#### C1 — Hardcoded Supabase Secrets in `.env` Committed to Git

> [!CAUTION]
> Real Supabase anon key and service-role key are in the tracked `.env` file.

- **File:** [.env:4-6](file:///c:/Users/adm/Desktop/Sinistrinha/.env#L4-L6)
- **Evidence:**
  ```
  SUPABASE_KEY=[REDACTED_ANON_KEY]
  SUPABASE_SERVICE_ROLE_KEY=[REDACTED_SERVICE_ROLE_KEY]
  ```
- **Impact:** Anyone with repo access has full Supabase admin. Service-role key bypasses RLS.
- **Fix:** (1) Rotate both keys immediately in Supabase dashboard. (2) Verify `.env` is in `.gitignore` (it is), but run `git rm --cached .env` to remove from history. (3) Consider `git filter-repo` to purge from all commits.

---

#### C2 — `FreeSpinView` and `LevelProgressView` Not Defined — Server Crash on Import

- **File:** [apps/game/urls.py:8-9](file:///c:/Users/adm/Desktop/Sinistrinha/apps/game/urls.py#L8-L9)
- **Evidence:**
  ```python
  from .views import (..., FreeSpinView, LevelProgressView)
  ```
  Neither class exists in `views.py` or anywhere in the codebase.
- **Impact:** Django **will not start** — `ImportError` on URL resolution. This blocks all functionality.
- **Fix:** Add the two missing view classes to `apps/game/views.py`:
  ```python
  class FreeSpinView(views.APIView):
      permission_classes = (IsAuthenticated,)
      def get(self, request):
          from .free_spins import FreeSpinSystem
          info = FreeSpinSystem().get_free_spin_info(request.user.profile)
          return Response(info)

  class LevelProgressView(views.APIView):
      permission_classes = (IsAuthenticated,)
      def get(self, request):
          profile = request.user.profile
          return Response({
              "level": profile.level, "xp": profile.xp,
              "free_spins": profile.free_spins,
          })
  ```

---

#### C3 — All Entry Points Default to `settings.dev` — Production Uses DEBUG Mode

- **Files:** [manage.py:6](file:///c:/Users/adm/Desktop/Sinistrinha/manage.py#L6), [asgi.py:8](file:///c:/Users/adm/Desktop/Sinistrinha/sinistrinha/asgi.py#L8), [wsgi.py:4](file:///c:/Users/adm/Desktop/Sinistrinha/sinistrinha/wsgi.py#L4), [celery.py:5](file:///c:/Users/adm/Desktop/Sinistrinha/sinistrinha/celery.py#L5)
- **Evidence:** All four files contain:
  ```python
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinistrinha.settings.dev')
  ```
- **Impact:** In production (Docker, Vercel), unless `DJANGO_SETTINGS_MODULE` is explicitly set, Django runs with `DEBUG=True`, `ALLOWED_HOSTS=['*']`, and `CORS_ALLOW_ALL_ORIGINS=True`.
- **Fix:** Change the default in `asgi.py`, `wsgi.py`, and `celery.py` to `sinistrinha.settings.prod`. Keep `manage.py` as `dev`. Add `DJANGO_SETTINGS_MODULE=sinistrinha.settings.prod` to docker-compose `environment:` blocks.

---

### 🟠 HIGH

#### H1 — `PlayerConsumer` Not Registered in WebSocket Routing

- **File:** [apps/casino/routing.py](file:///c:/Users/adm/Desktop/Sinistrinha/apps/casino/routing.py)
- **Evidence:** Only `CasinoConsumer` and `UserConsumer` are registered. `PlayerConsumer` (with JWT auth) is defined in `player_consumer.py` but never routed.
- **Impact:** Authenticated per-player WebSocket connections (`/ws/player/{id}/`) don't work. `NotificationService` sends to `player_{id}` group, but no consumer joins that group.
- **Fix:** Add to `routing.py`:
  ```python
  from .player_consumer import PlayerConsumer
  # Add:
  re_path(r'^ws/player/(?P<user_id>\d+)/$', PlayerConsumer.as_asgi()),
  ```

---

#### H2 — Jackpot Contribution in `SpinView` Has No `select_for_update` — Race Condition

- **File:** [apps/game/views.py:172-183](file:///c:/Users/adm/Desktop/Sinistrinha/apps/game/views.py#L172-L183)
- **Evidence:** `_contribute_to_jackpot` uses `get_or_create` + manual increment without `select_for_update`. The proper `JackpotSystem.contribute()` in `jackpot.py` *does* use `select_for_update`, but is never called.
- **Impact:** Under concurrent spins, jackpot contributions are lost (classic lost-update race).
- **Fix:** Replace `_contribute_to_jackpot` body with a call to `JackpotSystem().contribute(bet_amount)`.

---

#### H3 — `WithdrawView` Deducts Balance Before Verification — Funds Lost on Failure

- **File:** [apps/payments/views.py:42-43](file:///c:/Users/adm/Desktop/Sinistrinha/apps/payments/views.py#L42-L43)
- **Evidence:** Balance is deducted immediately (`profile.balance -= amount; profile.save()`), then a `PENDING` transaction is created. If the periodic task fails, the user has lost funds.
- **Impact:** Users lose money on failed withdrawals.
- **Fix:** Either (a) hold funds in a `frozen_balance` field until the task confirms, or (b) wrap the deduction and approval in a single atomic flow.

---

#### H4 — Supabase Env Vars Not Mapped to Django Settings

- **File:** [settings/base.py](file:///c:/Users/adm/Desktop/Sinistrinha/sinistrinha/settings/base.py)
- **Evidence:** `SUPABASE_URL`, `SUPABASE_KEY`, and `SUPABASE_SERVICE_ROLE_KEY` are read from `.env` but **never assigned to `settings.*`**. `supabase_client.py` reads them via `getattr(settings, 'SUPABASE_URL')` — which returns `None`.
- **Impact:** Supabase client silently initialises as `None`; all Realtime broadcasts fail.
- **Fix:** Add to `base.py`:
  ```python
  SUPABASE_URL = env('SUPABASE_URL', default='')
  SUPABASE_KEY = env('SUPABASE_KEY', default='')
  SUPABASE_SERVICE_ROLE_KEY = env('SUPABASE_SERVICE_ROLE_KEY', default='')
  ```

---

#### H5 — `socket.io-client` Incompatible with Django Channels WebSockets

- **File:** [frontend/package.json:24](file:///c:/Users/adm/Desktop/Sinistrinha/frontend/package.json#L24)
- **Evidence:** `"socket.io-client": "^4.8.3"` — Socket.IO uses its own transport protocol (EIO), not raw WebSocket frames.
- **Impact:** Frontend WebSocket connections will fail handshake with Django Channels.
- **Fix:** Remove `socket.io-client`; use the browser-native `WebSocket` API or a library like `reconnecting-websocket`.

---

### 🟡 MEDIUM

#### M1 — No Healthcheck for Django `web` Service

- **File:** [docker-compose.yml:4-17](file:///c:/Users/adm/Desktop/Sinistrinha/docker-compose.yml#L4-L17)
- **Evidence:** `probability_engine` has a healthcheck, but `web` and `redis` do not.
- **Fix:** Add to `web`:
  ```yaml
  healthcheck:
    test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/docs/')"]
    interval: 30s
    timeout: 5s
    retries: 3
  ```

---

#### M2 — No `depends_on` with `condition: service_healthy`

- **File:** [docker-compose.yml](file:///c:/Users/adm/Desktop/Sinistrinha/docker-compose.yml)
- **Evidence:** `web` depends on `redis` and `probability_engine` but with no health condition. If Redis isn't ready, Daphne crashes on channel-layer init.
- **Fix:** Add `condition: service_healthy` to each `depends_on` entry; add healthchecks to `redis` and `web`.

---

#### M3 — Nginx Missing Security Headers

- **File:** [nginx.conf](file:///c:/Users/adm/Desktop/Sinistrinha/nginx.conf)
- **Fix:** Add inside `server {}`:
  ```nginx
  add_header X-Frame-Options "DENY" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header Referrer-Policy "strict-origin-when-cross-origin" always;
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
  ```

---

#### M4 — Production Settings Missing HSTS

- **File:** [settings/prod.py](file:///c:/Users/adm/Desktop/Sinistrinha/sinistrinha/settings/prod.py)
- **Evidence:** No `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, or `SECURE_HSTS_PRELOAD`.
- **Fix:** Add:
  ```python
  SECURE_HSTS_SECONDS = 31536000
  SECURE_HSTS_INCLUDE_SUBDOMAINS = True
  SECURE_HSTS_PRELOAD = True
  SECURE_CONTENT_TYPE_NOSNIFF = True
  ```

---

#### M5 — `process_pending_withdrawals` Auto-Approves All Pending — No Validation

- **File:** [apps/payments/tasks.py:12](file:///c:/Users/adm/Desktop/Sinistrinha/apps/payments/tasks.py#L12)
- **Evidence:** `pending.update(status=TransactionStatus.COMPLETED)` — blanket approval.
- **Impact:** All withdrawals are silently approved without any anti-fraud or KYC check.

---

#### M6 — Probability Engine State is In-Memory — Lost on Restart

- **File:** [probability_engine/main.py:50-54](file:///c:/Users/adm/Desktop/Sinistrinha/probability_engine/main.py#L50-L54)
- **Evidence:** `house_edge`, `learning_agent`, `wins_simulator` are all in-process Python objects.
- **Impact:** Every container restart resets all session stats, behavioural profiles, and RTP convergence data.

---

#### M7 — Frontend Is Still Vite Boilerplate — Not Integrated

- **File:** [frontend/src/App.tsx](file:///c:/Users/adm/Desktop/Sinistrinha/frontend/src/App.tsx)
- **Evidence:** The `App.tsx` is the default Vite "Get started" page while `main.tsx` imports `GamePage`, `LoginPage`, etc. — the router is set up but `App.tsx` is dead code.
- **Impact:** Depending on which component is the entry point, the user either sees boilerplate or the actual game.

---

#### M8 — Docker Copies Entire Workspace Including `.env`, `venv/`, `node_modules/`

- **File:** [Dockerfile:7](file:///c:/Users/adm/Desktop/Sinistrinha/Dockerfile#L7)
- **Evidence:** `COPY . /app/` with no `.dockerignore`.
- **Fix:** Create `.dockerignore`:
  ```
  .env
  .git
  venv/
  .venv/
  frontend/node_modules/
  __pycache__/
  *.pyc
  ```

---

### 🟢 LOW

#### L1 — `version: '3.8'` in docker-compose is deprecated
- **File:** [docker-compose.yml:1](file:///c:/Users/adm/Desktop/Sinistrinha/docker-compose.yml#L1)
- **Fix:** Remove the `version:` key entirely (modern Compose doesn't need it).

#### L2 — `.env.example` Still Contains Real Supabase URL
- **File:** [.env.example:6](file:///c:/Users/adm/Desktop/Sinistrinha/.env.example#L6)
- **Fix:** Replace with `https://your-project.supabase.co`.

#### L3 — `UserConsumer` Accepts Any `user_id` Without Authentication
- **File:** [apps/casino/consumers.py:49-57](file:///c:/Users/adm/Desktop/Sinistrinha/apps/casino/consumers.py#L49-L57)
- **Impact:** Any client can connect to `ws/user/1/` and receive another user's private events.
- **Fix:** Require JWT token validation like `PlayerConsumer` does, or remove `UserConsumer` in favour of `PlayerConsumer`.

#### L4 — `STATICFILES_STORAGE` Deprecated in Django 5.x
- **File:** [settings/base.py:116](file:///c:/Users/adm/Desktop/Sinistrinha/sinistrinha/settings/base.py#L116)
- **Fix:** Use `STORAGES = {"staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}}`.

---

## 3. Security Hardening Profile

### Production-Ready `settings/prod.py` Additions

```python
# --- Add these to prod.py ---

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content security
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Proxy trust (behind nginx)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Session hardening
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# JWT tightening (reduce access token lifetime)
SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(minutes=15)
```

### Dependency Risk Patterns

| Package | Risk | Recommendation |
|---|---|---|
| `bleach>=6.1.0` | Listed in requirements but never imported | Remove or integrate for HTML sanitization |
| `django-otp>=1.2.2` | Listed but not in `INSTALLED_APPS` | Either configure 2FA or remove |
| `django-allauth>=0.61.1` | Listed but not in `INSTALLED_APPS` | Remove or integrate |
| `django-csp>=3.7` | Listed but CSP middleware not in `MIDDLEWARE` | Add `csp.middleware.CSPMiddleware` |
| No version pins | `Django>=5.0,<6.0` is wide | Pin to specific minor versions |

---

## 4. Test Gap Analysis

### Current Test Coverage

| Area | Test Files | Tests | Coverage |
|---|---|---|---|
| Game services | `test_bonus_service.py`, `test_level_service.py` | ~12 | Unit |
| Game integration | `test_spin_integration.py` | ~8 | Integration |
| Probability engine | `test_rtp.py` | ~6 | Statistical |
| Integration (root) | `test_free_spins.py`, `test_full_spin_flow.py`, `test_house_edge.py`, `test_jackpot.py` | ~20 | Integration |
| WebSocket consumers | `test_consumers.py` | ~6 | Unit |

### Critical Gaps

| Priority | Gap | Proposed File |
|---|---|---|
| 🔴 P0 | Auth endpoints (register/login/logout/refresh) | `tests/test_auth_api.py` |
| 🔴 P0 | Payment endpoints (deposit/withdraw) — race conditions | `tests/test_payments_api.py` |
| 🔴 P0 | Spin endpoint negative cases (insufficient balance, invalid bet) | `apps/game/tests/test_spin_edge_cases.py` |
| 🟠 P1 | Concurrent spin race condition (double-spend) | `tests/test_concurrency.py` |
| 🟠 P1 | WebSocket auth bypass on `UserConsumer` | `apps/casino/tests/test_ws_auth.py` |
| 🟠 P1 | Probability engine API contract tests | `probability_engine/tests/test_api_contract.py` |
| 🟡 P2 | Frontend → Backend integration (Vite proxy, API calls) | `frontend/src/__tests__/api.test.ts` |
| 🟡 P2 | Docker smoke test (compose up → health) | `tests/test_docker_smoke.sh` |
| 🟡 P2 | Withdrawal task fraud scenarios | `apps/payments/tests/test_withdrawal_task.py` |
| 🟢 P3 | Admin dashboard renders without errors | `apps/game/tests/test_admin_dashboard.py` |

### Top-10 Highest-Value Tests to Implement First

1. **`test_spin_requires_auth`** — Spin endpoint returns 401 without JWT
2. **`test_spin_insufficient_balance`** — Returns 400 when balance < bet
3. **`test_register_creates_profile`** — Register endpoint creates User + UserProfile
4. **`test_login_returns_tokens`** — Login returns access + refresh tokens
5. **`test_deposit_updates_balance`** — Deposit increases user balance atomically
6. **`test_withdraw_insufficient_balance`** — Withdraw returns 400 if underfunded
7. **`test_concurrent_spins_no_double_spend`** — Two parallel spins don't overdraft
8. **`test_probability_spin_contract`** — FastAPI `/probability/spin` returns expected schema
9. **`test_probability_health`** — `/health` returns `{"status": "ok"}`
10. **`test_user_consumer_rejects_unauthenticated`** — WS connection without token is closed

---

## 5. GitHub Issue Backlog

### 🔴 Critical

| # | Title | Owner | Effort |
|---|---|---|---|
| 1 | **Rotate leaked Supabase secrets and purge from git history** | DevOps | S |
| 2 | **Fix `ImportError`: Add missing `FreeSpinView` and `LevelProgressView`** | Backend | S |
| 3 | **Change default `DJANGO_SETTINGS_MODULE` to `prod` in production entry points** | Backend | S |

<details><summary>Issue 1 — Rotate Supabase Secrets</summary>

**Problem:** Supabase anon key, service-role key, and project URL are committed in `.env` and `.env.example`.
**Impact:** Full admin access to the database for anyone with repo access.
**Reproduction:** `cat .env` — keys are visible in plaintext.
**Acceptance Criteria:**
- [ ] Keys rotated in Supabase dashboard
- [ ] `.env` removed from git history (`git filter-repo`)
- [ ] `.env.example` uses placeholder values only
- [ ] CI/CD uses environment-injected secrets

</details>

<details><summary>Issue 2 — Fix ImportError on Missing Views</summary>

**Problem:** `apps/game/urls.py` imports `FreeSpinView` and `LevelProgressView` from `views.py`, but neither class exists.
**Impact:** Django cannot start — total downtime.
**Reproduction:** `python manage.py runserver` → `ImportError`.
**Acceptance Criteria:**
- [ ] Both view classes implemented in `views.py`
- [ ] Corresponding test coverage added
- [ ] Server starts without errors

</details>

<details><summary>Issue 3 — Production Defaults to Dev Settings</summary>

**Problem:** `asgi.py`, `wsgi.py`, and `celery.py` all default to `sinistrinha.settings.dev`.
**Impact:** Production runs with `DEBUG=True`, `ALLOWED_HOSTS=['*']`, `CORS_ALLOW_ALL_ORIGINS=True`.
**Acceptance Criteria:**
- [ ] `asgi.py`, `wsgi.py`, `celery.py` default to `settings.prod`
- [ ] `docker-compose.yml` sets `DJANGO_SETTINGS_MODULE` explicitly
- [ ] `manage.py` keeps `settings.dev` for local development

</details>

### 🟠 High

| # | Title | Owner | Effort |
|---|---|---|---|
| 4 | **Register `PlayerConsumer` in WebSocket routing** | Backend | S |
| 5 | **Fix jackpot race condition — use `JackpotSystem.contribute()`** | Backend | S |
| 6 | **Fix withdrawal fund-loss on failure** | Backend | M |
| 7 | **Map Supabase env vars to Django settings** | Backend | S |
| 8 | **Replace `socket.io-client` with native WebSocket** | Frontend | M |

### 🟡 Medium

| # | Title | Owner | Effort |
|---|---|---|---|
| 9 | **Add healthchecks for `web` and `redis` in docker-compose** | DevOps | S |
| 10 | **Add `depends_on` health conditions** | DevOps | S |
| 11 | **Add security headers to nginx.conf** | DevOps | S |
| 12 | **Add HSTS + session hardening to prod settings** | Backend | S |
| 13 | **Add `.dockerignore` to prevent secret/venv leakage** | DevOps | S |
| 14 | **Implement proper withdrawal validation in Celery task** | Backend | L |
| 15 | **Persist probability engine state to Redis** | Backend | L |

### 🟢 Low

| # | Title | Owner | Effort |
|---|---|---|---|
| 16 | **Remove deprecated `version:` from docker-compose** | DevOps | S |
| 17 | **Replace real Supabase URL in `.env.example`** | DevOps | S |
| 18 | **Require JWT auth on `UserConsumer` or deprecate it** | Backend | M |
| 19 | **Migrate `STATICFILES_STORAGE` to `STORAGES` dict** | Backend | S |
| 20 | **Remove unused deps: `bleach`, `django-otp`, `django-allauth`** | Backend | S |
| 21 | **Add CSP middleware since `django-csp` is installed** | Backend | S |
| 22 | **Clean up vestigial `App.tsx` boilerplate** | Frontend | S |

---

## 6. 7-Day Remediation Plan

### Day 1 — 🔴 Secrets & Server Boot (Issues 1, 2, 3)

- [ ] Rotate Supabase keys, purge `.env` from git history
- [ ] Implement `FreeSpinView` and `LevelProgressView`
- [ ] Fix `DJANGO_SETTINGS_MODULE` defaults in prod entry points
- [ ] Verify: `docker-compose up` starts all services without crashes

### Day 2 — 🟠 Data Integrity (Issues 5, 6, 7)

- [ ] Replace inline jackpot contribution with `JackpotSystem.contribute()`
- [ ] Fix withdrawal flow to freeze funds before approval
- [ ] Map Supabase env vars to Django settings
- [ ] Write tests: `test_concurrent_spins_no_double_spend`, `test_withdraw_insufficient_balance`

### Day 3 — 🟠 Real-Time & Frontend (Issues 4, 8)

- [ ] Register `PlayerConsumer` in WebSocket routing
- [ ] Replace `socket.io-client` with native WebSocket
- [ ] Write tests: `test_user_consumer_rejects_unauthenticated`

### Day 4 — 🟡 Security Hardening (Issues 11, 12, 13, 21)

- [ ] Add security headers to `nginx.conf`
- [ ] Add HSTS and session flags to `prod.py`
- [ ] Create `.dockerignore`
- [ ] Add CSP middleware to `MIDDLEWARE`
- [ ] Run Django `check --deploy` and fix all warnings

### Day 5 — 🟡 Reliability (Issues 9, 10, 14)

- [ ] Add healthchecks and health-conditions to docker-compose
- [ ] Implement proper withdrawal validation logic
- [ ] Write: `test_docker_smoke.sh` script

### Day 6 — 🟢 Cleanup & Test Coverage (Issues 16-22 + Test Plan)

- [ ] Remove deprecated compose version, stale deps, boilerplate `App.tsx`
- [ ] Fix `STATICFILES_STORAGE` deprecation
- [ ] Implement top-10 test cases from test plan
- [ ] Secure or remove `UserConsumer`

### Day 7 — Verification & Documentation

- [ ] Full `docker-compose up` smoke test
- [ ] Run complete test suite
- [ ] Update `README.md` with corrected setup instructions
- [ ] Update `ARCHITECTURE.md` with port matrix and service diagram
- [ ] Final PR review and merge
