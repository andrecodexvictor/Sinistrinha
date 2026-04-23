# Changelog: Integração e Remediação de Auditoria

Este documento detalha as mudanças significativas realizadas para integrar o frontend ao backend e corrigir as 22 vulnerabilidades identificadas no relatório de auditoria técnica.

## 🚀 Mudanças de Integração (Frontend ↔ Backend)

- **Autenticação Real:** Migração de mocks para autenticação JWT completa.
- **Store Sync:** Sincronização dos estados de saldo, nível e XP entre `authStore`, `gameStore` e `casinoStore`.
- **API Client:** Implementação de um cliente Axios centralizado com interceptadores para refresh automático de tokens.
- **WebSockets:** Conexão real com o servidor de WebSockets para feeds de ganhos globais e atualizações privadas do jogador.
- **Tipagem:** Alinhamento completo das interfaces TypeScript com os Serializers do Django REST Framework.

## 🛡️ Remediação de Auditoria (Principais Correções)

### Críticas (🔴)
- **C1 (Segredos):** Instruções para rotação de chaves implementadas; `.env.example` sanitizado.
- **C2 (Server Crash):** Implementadas as views faltantes (`FreeSpinView`, `LevelProgressView`) que impediam o Django de iniciar.
- **C3 (Prod Settings):** Configuração de `DJANGO_SETTINGS_MODULE` corrigida para padrão `prod` em ambientes produtivos (ASGI, WSGI, Celery).

### Alta Prioridade (🟠)
- **H1 (Routing):** Registro do `PlayerConsumer` no roteamento de WebSockets.
- **H2 (Race Condition):** Proteção contra condições de corrida no Jackpot usando `select_for_update`.
- **H3 (Data Loss):** Fluxo de saque tornado atômico para evitar perda de fundos em caso de erro.
- **H4 (Settings):** Mapeamento de variáveis de ambiente do Supabase nas configurações do Django.
- **H5 (Compatibility):** Remoção do `socket.io-client` em favor de WebSockets nativos.

### Média e Baixa Prioridade (🟡/🟢)
- **M1/M2 (Docker):** Adição de healthchecks e condições de dependência no Docker Compose.
- **M3 (Nginx):** Adição de headers de segurança e configuração de proxy para o frontend.
- **M4 (Hardening):** Ativação de HSTS, cookies seguros e redução de tempo de vida do token JWT.
- **M8 (Dockerignore):** Prevenção de vazamento de arquivos locais (`.env`, `venv`, `node_modules`) para imagens Docker.
- **L4 (Storages):** Migração para a nova sintaxe `STORAGES` do Django 5.0.

## ⚙️ CI/CD

Implementação de pipeline GitHub Actions com:
1. Testes de Backend.
2. Build e Lint de Frontend.
3. Scan de Segurança (Bandit, npm audit, Secrets check).
4. Smoke Test em Docker.

---
*Comprometido em 23/04/2026*
