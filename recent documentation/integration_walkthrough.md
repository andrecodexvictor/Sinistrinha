# Sinistrinha Integration Walkthrough

> Complete audit report, changes implemented, and verification guide.

## 1. Root Causes Found (Pre-Fix)

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | `FreeSpinView` and `LevelProgressView` imported in `urls.py` but never defined — **Django crashes on startup** | 🔴 Critical | ✅ Fixed |
| 2 | All frontend pages use `setTimeout` mocks — **zero backend connectivity** | 🔴 Critical | ✅ Fixed |
| 3 | Frontend `SpinResult` schema mismatches backend `SpinResponseSerializer` fields | 🟠 High | ✅ Fixed |
| 4 | No Axios client or JWT interceptor — frontend cannot authenticate | 🟠 High | ✅ Fixed |
| 5 | Vite has no proxy config — CORS blocks all local dev API calls | 🟠 High | ✅ Fixed |
| 6 | LoginModal/LoginPage send `email` but SimpleJWT expects `username` | 🟠 High | ✅ Fixed |
| 7 | `CORS_ALLOW_CREDENTIALS` missing in Django settings | 🟡 Medium | ✅ Fixed |
| 8 | `CSRF_TRUSTED_ORIGINS` not configured | 🟡 Medium | ✅ Fixed |
| 9 | No `/health/` endpoint for Docker healthchecks | 🟡 Medium | ✅ Fixed |
| 10 | `.env.example` missing `VITE_*` and `CSRF_*` variables | 🟡 Medium | ✅ Fixed |
| 11 | No CI/CD pipeline | 🟡 Medium | ✅ Fixed |
| 12 | Hardcoded jackpot `R$ 25.480,90` in GamePage | 🟢 Low | ✅ Fixed |
| 13 | Header dropdown buttons non-functional (Perfil/Histórico) | 🟢 Low | ✅ Fixed |

## 2. Files Changed

### Backend Changes

| File | Change |
|------|--------|
| `apps/game/views.py` | Added `FreeSpinView` and `LevelProgressView` classes |
| `sinistrinha/urls.py` | Added `/health/` endpoint |
| `sinistrinha/settings/base.py` | Added `CORS_ALLOW_CREDENTIALS`, `CSRF_TRUSTED_ORIGINS` |
| `.env.example` | Added all required env vars with sections |

### Frontend Changes

| File | Change |
|------|--------|
| `frontend/src/lib/api.ts` | **NEW** — Axios client with JWT interceptor + auto-refresh |
| `frontend/.env` | **NEW** — `VITE_API_URL` and `VITE_WS_URL` |
| `frontend/vite.config.ts` | Added `/api` and `/ws` proxy rules |
| `frontend/src/types/user.types.ts` | Rewritten to match `UserProfileSerializer` |
| `frontend/src/types/api.types.ts` | Rewritten to match DRF response shapes |
| `frontend/src/types/game.types.ts` | Added `BackendSpinResponse`, updated `SpinResult`, added `backendToReels()` |
| `frontend/src/store/authStore.ts` | Rewritten — real JWT login/register/logout/refresh |
| `frontend/src/store/gameStore.ts` | Rewritten — real `POST /api/game/spin/`, syncs with auth store |
| `frontend/src/store/casinoStore.ts` | Rewritten — real WebSocket to `/ws/casino/`, player channel helper |
| `frontend/src/pages/LoginPage.tsx` | Real API login, field renamed `email` → `username` |
| `frontend/src/pages/RegisterPage.tsx` | Real API register + auto-login |
| `frontend/src/pages/WalletPage.tsx` | Real transaction fetch, deposit/withdraw actions |
| `frontend/src/pages/RankingPage.tsx` | Real leaderboard from `/api/user/leaderboard/` |
| `frontend/src/pages/HistoryPage.tsx` | Real spin history from `/api/game/user/history/` |
| `frontend/src/pages/GamePage.tsx` | Fetches real jackpot, syncs auth on mount |
| `frontend/src/components/layout/AppLayout.tsx` | Auth guard + session restore on mount |
| `frontend/src/components/layout/Header.tsx` | Uses auth store for balance, working nav links |
| `frontend/src/components/auth/LoginModal.tsx` | Real API call instead of `setTimeout` |

### Infrastructure Changes

| File | Change |
|------|--------|
| `.github/workflows/ci.yml` | **NEW** — Full CI/CD pipeline |
| `ARCHITECTURE.md` | **NEW** — System diagrams, endpoint map, auth flow |
| `README.md` | Updated with integration info, CI/CD, dev instructions |

## 3. Validation Steps

### Quick Smoke Test (Local)
```bash
# 1. Start backend
cd Sinistrinha
cp .env.example .env  # Update credentials
pip install -r requirements.txt
python manage.py migrate --settings=sinistrinha.settings.dev
python manage.py runserver 0.0.0.0:8000

# 2. Test health endpoint
curl http://localhost:8000/health/
# Expected: {"status": "ok", "service": "sinistrinha"}

# 3. Test login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"player1","password":"test1234"}'
# Expected: {"access": "eyJ...", "refresh": "eyJ..."}

# 4. Start frontend
cd frontend
npm install
npm run dev
# → Open http://localhost:3000/login
# → Login with player1 / test1234
# → Verify balance loads, spin button works
```

### Docker Smoke Test
```bash
chmod +x setup.sh
./setup.sh
# All services start, health checks pass
curl http://localhost:8000/health/
curl http://localhost:8001/health
```

## 4. Go-Live Checklist

- [x] Backend starts without `ImportError`
- [x] `/health/` endpoint responds
- [x] Frontend login calls real `/api/auth/login/`
- [x] JWT tokens stored and attached to requests
- [x] Spin button calls real `/api/game/spin/`
- [x] Balance/level updates reflected in UI after spin
- [x] Wallet page fetches real transactions
- [x] Ranking page fetches real leaderboard
- [x] History page fetches real spin history
- [x] WebSocket connects to `/ws/casino/` for live feed
- [x] CORS configured for localhost:3000 and localhost:5173
- [x] CSRF trusted origins configured
- [x] CI/CD pipeline created
- [x] Architecture documentation created
- [x] README updated

## 5. Connectivity Map

```
Frontend Call          → URL                    → Proxy Target        → Backend Handler
─────────────────────────────────────────────────────────────────────────────────────
authStore.loginAsync   → POST /api/auth/login/  → localhost:8000      → TokenObtainPairView
authStore.registerAsync→ POST /api/auth/register/→ localhost:8000     → RegisterView
authStore.fetchProfile → GET /api/user/profile/ → localhost:8000      → UserProfileView
gameStore.spin         → POST /api/game/spin/   → localhost:8000      → SpinView.post
gameStore.fetchJackpot → GET /api/game/jackpot/ → localhost:8000      → JackpotView
WalletPage             → GET /api/payments/transactions/ → :8000     → TransactionListView
RankingPage            → GET /api/user/leaderboard/ → :8000          → LeaderboardView
HistoryPage            → GET /api/game/user/history/ → :8000         → UserSpinHistoryView
casinoStore.connectWS  → WS /ws/casino/         → localhost:8000      → CasinoConsumer
playerWS               → WS /ws/user/{id}/      → localhost:8000      → PlayerConsumer
```
