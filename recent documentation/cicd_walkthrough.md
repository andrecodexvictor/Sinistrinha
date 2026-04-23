# Plano de Implementação e Walkthrough de CI/CD

Este documento descreve a implementação do pipeline de CI/CD (Integração e Entrega Contínuas) para o projeto Sinistrinha, baseado nas necessidades de automação e segurança levantadas nos relatórios de auditoria.

## 1. Visão Geral da Arquitetura de CI/CD

O pipeline foi construído utilizando **GitHub Actions** (`.github/workflows/ci.yml`) e é acionado automaticamente em dois cenários:
- Em **Push** para as branchs `main` e `develop`.
- Em **Pull Requests** apontando para a `main`.

O pipeline foi dividido em 4 **Jobs** paralelos e dependentes para maximizar a velocidade do feedback e garantir a estabilidade do código.

## 2. Walkthrough dos Jobs Implementados

### Job 1: Backend CI (Django)
*   **Ambiente:** Ubuntu Latest, Python 3.12, Redis 7 (serviço auxiliar acoplado).
*   **Ações Realizadas:**
    1. Instalação das dependências do `requirements.txt`.
    2. Geração de um `.env` limpo a partir do `.env.example`.
    3. Execução das migrações do banco de dados (valida a integridade do schema).
    4. `python manage.py check`: Validação estática de configurações do Django.
    5. `pytest`: Execução da suíte de testes unitários e de integração.
*   **Prevenção:** Impede que código com erros de sintaxe ou testes falhos chegue à produção.

### Job 2: Frontend CI (React + Vite)
*   **Ambiente:** Ubuntu Latest, Node.js 20.
*   **Ações Realizadas:**
    1. Instalação de pacotes via `npm ci` (garante as versões exatas do `package-lock.json`).
    2. Checagem rígida de tipagem TypeScript (`npx tsc --noEmit`).
    3. Análise estática com ESLint (`npm run lint`).
    4. Build de produção (`npm run build`).
*   **Prevenção:** Garante que o frontend compila corretamente e não possui erros de tipagem entre as chamadas da API (`BackendSpinResponse`) e os componentes UI.

### Job 3: Probability Engine CI (FastAPI)
*   **Ambiente:** Ubuntu Latest, Python 3.12.
*   **Ações Realizadas:**
    1. Instalação do FastAPI, Uvicorn e dependências do motor.
    2. Validação de inicialização rápida e verificação de erros de importação (`import main`).
*   **Prevenção:** Garante que o motor de cálculo matemático roda independentemente do monolito Django.

### Job 4: Docker Smoke Test (Validação End-to-End)
*   **Condição:** Roda apenas na branch `main` e depende que os Jobs 1 e 2 passem.
*   **Ações Realizadas:**
    1. Faz o build de todo o ecossistema (`docker compose build`).
    2. Levanta o Redis e o Probability Engine em background.
    3. Levanta a API Django (`web`) e o Nginx.
    4. Dispara requisições `curl` contra os endpoints `/health/` e `/health` (implementados durante a auditoria).
*   **Prevenção:** Garante que os containers se comunicam entre si (Networking) e que não há problemas de orquestração no Docker.

## 3. Plano de Melhorias Futuras (Next Steps)

Para atingir um nível de maturidade corporativa, o pipeline de CI/CD deve ser expandido nas seguintes direções:

1. **Continuous Deployment (CD) para a Vercel:**
   - Adicionar uma Action oficial da Vercel para subir automaticamente o artefato do Frontend (`/frontend/dist`) para o ambiente de produção/staging quando um merge ocorrer na `main`.

2. **Continuous Deployment (CD) para Render/AWS:**
   - Fazer o build e push das imagens Docker do Django e FastAPI para um Container Registry (ex: GitHub Packages).
   - Acionar webhooks de deploy (Render) ou atualizar task definitions (AWS ECS).

3. **Verificação de Segurança Integrada (DevSecOps):**
   - Implementar ferramentas como o *Bandit* (para Python) e *npm audit* para barrar Pull Requests que introduzam vulnerabilidades ou senhas hardcoded.
