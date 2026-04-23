# End-to-End Integration Plan: Sinistrinha

This plan addresses the full frontend-backend integration based on the audit findings of the current repository state.

## 1. End-to-End Integration Audit & Fixes

**Current State:**
*   The frontend is currently **completely mocked**. Components like `LoginPage`, `RegisterPage`, and `gameStore.ts` use `setTimeout` and local state instead of making real API requests.
*   **CRITICAL BACKEND BUG:** `apps/game/urls.py` imports `FreeSpinView` and `LevelProgressView`, but these are **not defined** in `apps/game/views.py`. This will cause an `ImportError` and crash the Django server on startup.

**Plan:**
*   **Fix Backend Crashing:** Implement or remove `FreeSpinView` and `LevelProgressView` in `apps/game/views.py` immediately.
*   **Implement API Client:** Set up `axios` in the frontend (e.g., `src/lib/api.ts`) configured with base URLs and interceptors for adding the JWT token to headers.
*   **Map Endpoints:**
    *   Auth: Replace mocks in `authStore.ts` to call `POST /api/auth/login/` and `POST /api/auth/register/`.
    *   Game: Replace mocks in `gameStore.ts` to call `POST /api/game/spin/`.
    *   Wallet: Replace mocks in `WalletPage.tsx` to call `GET /api/payments/transactions/`.
    *   Ranking: Replace mocks in `RankingPage.tsx` to call `GET /api/user/leaderboard/`.
    *   History: Replace mocks in `HistoryPage.tsx` to call `GET /api/game/user/history/`.

## 2. API Base URL and Environment Consistency

**Current State:**
*   `.env.example` defines `VITE_API_URL` and `VITE_WS_URL`, but Vite isn't configured to use them (no proxy in `vite.config.ts` and no usage in codebase).
*   Backend `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` are split across `base.py`, `dev.py`, and `prod.py` but look somewhat consistent.
*   `vercel.json` exists for frontend deployment.

**Plan:**
*   **Frontend Config:** Use `import.meta.env.VITE_API_URL` in the frontend API client.
*   **Vite Proxy:** Configure `vite.config.ts` to proxy API requests to the backend during local development (port 8000) to avoid CORS issues locally.
*   **Env Variables:** Standardize on `VITE_API_BASE_URL` and `VITE_WS_BASE_URL`.

## 3. CORS + CSRF Integration Hardening

**Current State:**
*   `corsheaders` is installed. `CORS_ALLOWED_ORIGINS` is configured.
*   Authentication relies on JWT, meaning CSRF is less of a concern for API requests (since cookies aren't used for auth), but if cookies were introduced, CSRF would be critical.
*   WebSocket connections require JWT token passing (currently passed via query string `?token=...` in `player_consumer.py`, which is fine for JWT).

**Plan:**
*   Ensure `CORS_ALLOW_CREDENTIALS` is explicitly configured if the strategy changes to HttpOnly cookies.
*   Validate CORS by making `OPTIONS` preflight requests in the regression test suite.

## 4. Contract Validation (Mismatches)

**Current State (High Risk):**
There is a massive contract mismatch between the mocked frontend and the actual backend implementation.
*   **Frontend `SpinResult` expects:** `winningLines`, `totalWin`, `xpGained`, `jackpot`.
*   **Backend `SpinResponseSerializer` returns:** `spin_id`, `payout`, `combination_type`, `is_jackpot`, `multiplier`, `free_spins_awarded`, `xp_earned`, `new_balance`, `new_level`, `winning_symbol`, etc.

**Plan:**
*   **Normalize Contracts:** We will adapt the **Frontend** to consume the Backend's schema.
*   Update `src/types/game.types.ts` to match `SpinResponseSerializer`.
*   Modify `gameStore.ts` to process `payout` instead of `totalWin` and map `combination_type` appropriately.

## 5. Authentication/Session Integration

**Current State:**
*   Backend uses `rest_framework_simplejwt`.
*   Frontend `authStore.ts` mocks login and stores arbitrary tokens.

**Plan:**
*   **Login Flow:** Frontend sends `email/password` to `/api/auth/login/`. Receives `access` and `refresh` tokens.
*   **Storage:** Store the `access` token in memory/state and the `refresh` token in `localStorage` (or preferably an HttpOnly cookie if security requirements increase).
*   **Axios Interceptor:** Automatically attach `Authorization: Bearer <token>` to all requests.
*   **Refresh Flow:** Automatically intercept `401 Unauthorized` responses, call `/api/auth/refresh/`, and retry the original request.

## 6. Integration Test Generation

**Plan:**
Implement a robust integration test suite using `pytest` for the backend:
1.  **Auth Flow:** Test successful login, failed login, token refresh, and logout.
2.  **Game Flow:** Test an authenticated spin request, verifying balance deductions and payout additions.
3.  **Invalid States:** Test spinning with insufficient balance.
4.  **Free Spins:** Test spinning with `use_free_spin=True` when available.
5.  **WebSockets:** Test connecting to `ws/user/{user_id}/` with a valid JWT.

## 7. Nginx Proxy Alignment

**Current State:**
*   `nginx.conf` has proxy passes to `web:8000` and `probability_engine:8001`.
*   `location /` proxies to `http://web`. This is incorrect if the frontend is a separate SPA running on Vercel or locally via Vite.

**Plan:**
*   Update `nginx.conf` so `location /` serves static frontend files or acts appropriately for the deployment target. If the frontend is on Vercel, Nginx shouldn't be routing `/` to the Django backend (unless Django serves the built SPA).
*   Ensure WebSocket `Upgrade` headers are properly forwarded for `/ws/`.

## 8. "Fix Highest-Impact Integration Bug Now"

**Bug:** `ImportError` on Django startup due to missing views.
**Root Cause:** `apps/game/urls.py` attempts to import `FreeSpinView` and `LevelProgressView` from `views.py`, but they don't exist.
**Impact:** CRITICAL. The backend cannot start.
**Fix Plan:**
1.  Open `apps/game/views.py`.
2.  Implement `FreeSpinView` to return available free spins for the user.
3.  Implement `LevelProgressView` to return current XP, Level, and XP required for the next level.
4.  Once fixed, begin replacing frontend mocks with real API calls using Axios.
