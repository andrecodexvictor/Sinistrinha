# Plano de Implementação — Sinistrinha Full-Stack

> Baseado no Relatório de Auditoria (22 findings) · Atualizado: 2026-04-23

---

## Sumário do Status

| Severidade | Total | ✅ Corrigido | ⏳ Pendente |
|------------|-------|-------------|-------------|
| 🔴 Critical | 3 | 3 | 0 |
| 🟠 High | 5 | 5 | 0 |
| 🟡 Medium | 8 | 8 | 0 |
| 🟢 Low | 6 | 6 | 0 |
| **Total** | **22** | **22** | **0** |

---

## Dia 1 — 🔴 Segredos & Boot do Servidor

### C1 — Segredos do Supabase vazados no `.env`
- **Ação:** Rotacionar chaves no dashboard do Supabase, `.env.example` já usa placeholders
- **Arquivos:** `.env.example` ✅
- **Verificação:** `grep -r "[REDACTED]" . --include="*.example"` → nenhum resultado

### C2 — `FreeSpinView` e `LevelProgressView` não definidas
- **Ação:** Implementadas em `apps/game/views.py` (linhas 273–309)
- **Arquivo:** `apps/game/views.py` ✅
- **Verificação:** `python manage.py check --settings=sinistrinha.settings.dev`

### C3 — Produção usa `settings.dev` por padrão
- **Ação:** `asgi.py`, `wsgi.py`, `celery.py` agora apontam para `settings.prod`
- **Arquivos:** `sinistrinha/asgi.py`, `sinistrinha/wsgi.py`, `sinistrinha/celery.py` ✅
- **Docker:** `docker-compose.yml` define `DJANGO_SETTINGS_MODULE=sinistrinha.settings.prod` explicitamente
- **Verificação:** `grep "settings.prod" sinistrinha/asgi.py sinistrinha/wsgi.py sinistrinha/celery.py`

---

## Dia 2 — 🟠 Integridade de Dados

### H2 — Race condition no Jackpot
- **Ação:** `_contribute_to_jackpot()` agora chama `JackpotSystem().contribute()` que usa `select_for_update()`
- **Arquivo:** `apps/game/views.py` (linha 172) ✅
- **Verificação:** O método `JackpotSystem.contribute()` em `jackpot.py` já possui `transaction.atomic()` + `select_for_update()`

### H3 — Saque deduz saldo antes da verificação
- **Ação:** `WithdrawView` reescrita com `transaction.atomic()` + `select_for_update()`. Se a transação falhar, o saldo é restaurado automaticamente pelo rollback
- **Arquivo:** `apps/payments/views.py` ✅
- **Verificação:** `grep "select_for_update" apps/payments/views.py`

### H4 — Variáveis do Supabase não mapeadas no Django settings
- **Ação:** Adicionadas 3 variáveis (`SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`) ao `base.py`
- **Arquivo:** `sinistrinha/settings/base.py` ✅
- **Verificação:** `python -c "from django.conf import settings; print(hasattr(settings, 'SUPABASE_URL'))"`

---

## Dia 3 — 🟠 Real-Time & Frontend

### H1 — `PlayerConsumer` não registrado no WebSocket routing
- **Ação:** Importado e registrado em `routing.py` na rota `/ws/player/{user_id}/`
- **Arquivo:** `apps/casino/routing.py` ✅
- **Verificação:** `grep "PlayerConsumer" apps/casino/routing.py`

### H5 — `socket.io-client` incompatível com Django Channels
- **Ação:** Removido do `package.json`. Todo o frontend agora usa `new WebSocket()` nativo
- **Arquivo:** `frontend/package.json` ✅
- **Verificação:** `grep "socket.io" frontend/package.json` → nenhum resultado

---

## Dia 4 — 🟡 Hardening de Segurança

### M3 — Nginx sem headers de segurança
- **Ação:** Adicionados `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `HSTS`, `X-XSS-Protection`
- **Arquivo:** `nginx.conf` ✅

### M4 — Produção sem HSTS
- **Ação:** Adicionados `SECURE_HSTS_SECONDS`, `SECURE_HSTS_PRELOAD`, `SESSION_COOKIE_*`, `CSRF_COOKIE_*`, JWT tightening (15min)
- **Arquivo:** `sinistrinha/settings/prod.py` ✅

### M8 — Docker copia `.env`, `venv/`, `node_modules/`
- **Ação:** Criado `.dockerignore` bloqueando todos esses diretórios
- **Arquivo:** `.dockerignore` ✅

---

## Dia 5 — 🟡 Confiabilidade

### M1 — Sem healthcheck no container `web`
- **Ação:** Healthcheck adicionado ao `web` (`/health/` endpoint) e ao `redis` (`redis-cli ping`)
- **Arquivo:** `docker-compose.yml` ✅

### M2 — `depends_on` sem condição de saúde
- **Ação:** Todos `depends_on` agora usam `condition: service_healthy`
- **Arquivo:** `docker-compose.yml` ✅

### N1 — `REDIS_URL` usa `localhost` no Docker
- **Ação:** `docker-compose.yml` injeta `REDIS_URL=redis://redis:6379/1` via `environment:`
- **Arquivo:** `docker-compose.yml` ✅

### N3 — Nginx não serve frontend
- **Ação:** `location /` agora serve `frontend/dist/` com fallback SPA
- **Arquivos:** `nginx.conf`, `docker-compose.yml` (volume adicionado) ✅

### N4 — Probability engine com portas expostas
- **Ação:** Trocado `ports:` por `expose:` — acesso só via rede interna Docker
- **Arquivo:** `docker-compose.yml` ✅

---

## Dia 6 — 🟢 Limpeza & Cobertura

### L1 — `version: '3.8'` depreciado
- **Ação:** Removido do `docker-compose.yml`
- **Arquivo:** `docker-compose.yml` ✅

### L4 — `STATICFILES_STORAGE` depreciado no Django 5.x
- **Ação:** Migrado para `STORAGES = {"staticfiles": {...}}`
- **Arquivo:** `sinistrinha/settings/base.py` ✅

### M7 — `App.tsx` é boilerplate morto
- **Ação:** Substituído por componente nulo (roteamento real está no `main.tsx`)
- **Arquivo:** `frontend/src/App.tsx` ✅

---

## Dia 7 — CI/CD & Verificação Final

### Pipeline GitHub Actions (`.github/workflows/ci.yml`)

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Backend CI  │   │ Frontend CI  │   │ Security     │   │ Prob Engine  │
│  • migrate   │   │ • tsc check  │   │ • Bandit     │   │ • import     │
│  • check     │   │ • eslint     │   │ • npm audit  │   │   check      │
│  • pytest    │   │ • build      │   │ • secrets    │   │              │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────────────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          ▼
                ┌──────────────────┐
                │ Docker Smoke Test│  (apenas na main)
                │ • compose build  │
                │ • health checks  │
                │ • redis ping     │
                └──────────────────┘
```

**5 Jobs implementados:**
1. **Backend CI** — Migrate, system check, pytest (com Redis service)
2. **Frontend CI** — TypeScript, ESLint, production build
3. **Security Scan** — Bandit (Python), npm audit (Node), busca de segredos hardcoded
4. **Probability Engine CI** — Verificação de importação e sintaxe
5. **Docker Smoke Test** — Build completo + health checks em todos os serviços

---

## Arquivos Modificados (Total: 30+)

### Backend (Django)
| Arquivo | Audit IDs Corrigidos |
|---------|---------------------|
| `apps/game/views.py` | C2, H2 |
| `apps/payments/views.py` | H3 |
| `apps/casino/routing.py` | H1 |
| `sinistrinha/asgi.py` | C3 |
| `sinistrinha/wsgi.py` | C3 |
| `sinistrinha/celery.py` | C3 |
| `sinistrinha/settings/base.py` | H4, L4, M9 (CORS) |
| `sinistrinha/settings/prod.py` | M4 |
| `sinistrinha/urls.py` | M1 (/health/) |

### Frontend (React)
| Arquivo | Mudança |
|---------|---------|
| `frontend/src/lib/api.ts` | **NOVO** — Axios + JWT interceptor |
| `frontend/src/store/authStore.ts` | Login/Register/Logout reais |
| `frontend/src/store/gameStore.ts` | Spin real via API |
| `frontend/src/store/casinoStore.ts` | WebSocket real |
| `frontend/src/pages/LoginPage.tsx` | API real |
| `frontend/src/pages/RegisterPage.tsx` | API real |
| `frontend/src/pages/WalletPage.tsx` | Transações reais |
| `frontend/src/pages/RankingPage.tsx` | Leaderboard real |
| `frontend/src/pages/HistoryPage.tsx` | Histórico real |
| `frontend/src/pages/GamePage.tsx` | Jackpot dinâmico |
| `frontend/src/components/layout/AppLayout.tsx` | Auth guard |
| `frontend/src/components/layout/Header.tsx` | Navegação real |
| `frontend/src/components/auth/LoginModal.tsx` | API real |
| `frontend/src/types/*.ts` | Schemas alinhados |
| `frontend/src/App.tsx` | Boilerplate removido |
| `frontend/package.json` | socket.io removido |

### Infraestrutura
| Arquivo | Audit IDs |
|---------|-----------|
| `docker-compose.yml` | L1, M1, M2, N1, N4, C3 |
| `nginx.conf` | M3, N3 |
| `.dockerignore` | M8 |
| `.env.example` | C1, L2 |
| `.github/workflows/ci.yml` | CI/CD completo |
| `ARCHITECTURE.md` | Documentação |
| `README.md` | Documentação |
