# Sinistrinha — Probability Engine 🦍🎰

Microserviço de probabilidade e inteligência adaptativa para o jogo **Sinistrinha**.

## Arquitetura

```
probability_engine/
├── config.py            # Símbolos, pesos, tabela de pagamentos, constantes
├── weight_engine.py     # Motor de roletas virtuais (WeightEngine)
├── payout_calculator.py # Cálculo de combinações e pagamentos (PayoutCalculator)
├── house_edge.py        # Controlador dinâmico de RTP (HouseEdgeController)
├── learning_agent.py    # Perfil comportamental e recomendações (AdaptiveLearningAgent)
├── simulator.py         # Feed de vitórias recentes (RecentWinsSimulator)
├── main.py              # FastAPI — endpoints REST
├── Dockerfile
├── requirements.txt
└── tests/
    └── test_rtp.py      # Simulações Monte Carlo + testes unitários
```

## Símbolos do Jogo

| Símbolo | Ícone | Peso | Multiplicador | Tipo |
|---------|-------|------|---------------|------|
| Pendrive | 🔌 | 35 | 1.5× | Comum |
| Mouse | 🖱️ | 30 | 2.0× | Comum |
| Teclado | ⌨️ | 28 | 2.5× | Comum |
| RAM | 💾 | 18 | 5.0× | Médio |
| SSD | 💿 | 15 | 8.0× | Médio |
| Monitor | 🖥️ | 12 | 12.0× | Médio |
| CPU | 🔲 | 8 | 25.0× | Raro |
| GPU RTX | 🎮 | 5 | 50.0× | Raro |
| Gorila Dourado | 🦍 | 2 | 150.0× | Ultra-raro |
| Wild Sinistrinha | 🃏 | 3 | — | Wild |
| Scatter Banana | 🍌 | 4 | — | Scatter |

## Algoritmos Principais

### 1. WeightEngine (Pesos por Roleta)

Cada uma das 5 roletas possui uma **strip virtual independente**. As roletas extremas (0 e 4) inflam símbolos comuns em +15% e deflacionam raros em −20%. A roleta central (2) inflaciona raros em +10% para produzir **near-misses** convincentes.

### 2. PayoutCalculator (Combinações)

Avaliação **esquerda-para-direita adjacente**:
- **5 iguais** = jackpot (100% do multiplicador)
- **4 iguais** = 70% do multiplicador
- **3 iguais** = 40% do multiplicador
- **Wild** completa combos com bônus de +20%
- **Scatters** contados globalmente: 2→2 free spins, 3→5, 4→8, 5→12

### 3. HouseEdgeController (RTP Dinâmico)

O RTP alvo é **87%** (13% house edge), ajustável por nível do usuário (85%–89.5%).

Técnicas implementadas:
1. **Convergência de RTP** — compara RTP da sessão com target e ajusta modifier
2. **Detecção de Streaks** — sequências de vitórias apertam; sequências de derrotas afrouxam
3. **Ciclos de Volatilidade** — alterna entre fases "hot", "normal" e "cold"
4. **Proteção de Budget** — quando o jogador perde >70% do budget, o sistema eases para evitar churn
5. **Near-Miss Forçado** — degrada jackpots para "quase acertos" com probabilidade configurável

### 4. AdaptiveLearningAgent (Mente do Usuário)

Perfil comportamental usando **EWMA** (Exponentially Weighted Moving Average):
- `avg_bet` — aposta média
- `bet_escalation_score` — escalação de apostas após derrotas
- `spin_velocity` — spins por minuto
- `churn_risk` — risco de abandono (0–1)
- `player_type` — whale / high_roller / grinder / cautious / regular

Gatilhos psicológicos ativos:
- **Variable Ratio Reinforcement** — recompensas espaçadas irregularmente
- **Loss Aversion Exploitation** — ajuste quando o jogador está prestes a sair
- **Near-Miss Effect** — integrado com HouseEdgeController
- **Escalation of Commitment** — detectado via bet_escalation_score

### 5. RecentWinsSimulator (Feed FOMO)

Gera feed misto de vitórias **reais** e **simuladas** com nomes brasileiros e cidades reais, formatando como "R$ 1.247,00 em RAM DDR5" para máximo impacto visual.

## API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/probability/spin` | Executa um spin |
| `GET` | `/probability/user-report/{user_id}` | Relatório comportamental |
| `GET` | `/probability/recent-wins` | Feed de vitórias (FOMO) |
| `POST` | `/probability/update-weights` | Atualiza estatísticas globais |
| `GET` | `/probability/stats` | RTP global e métricas |
| `GET` | `/health` | Liveness probe |

### Exemplo de Spin

```bash
curl -X POST http://localhost:8001/probability/spin \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "bet_amount": 10.0,
    "user_level": 5,
    "display_name": "Lucas_TI",
    "initial_budget": 100.0
  }'
```

Resposta inclui: `reels`, `reel_icons`, `payout`, `modifier_used`, `near_miss_forced`, `session_rtp`, `reasoning`, `active_triggers`.

## Observabilidade

Cada spin loga em detalhes:
- Modifier aplicado e motivo (convergência RTP, streak, volatilidade)
- Técnica psicológica ativa
- RTP da sessão vs target
- Se near-miss foi forçado ou natural
- Perfil comportamental atual

## Executando

```bash
# Instalar dependências
pip install -r probability_engine/requirements.txt

# Rodar o servidor
uvicorn probability_engine.main:app --host 0.0.0.0 --port 8001 --reload

# Rodar testes
pytest probability_engine/tests/ -v -s
```

## Docker

```bash
docker build -f probability_engine/Dockerfile -t sinistrinha-probability .
docker run -p 8001:8001 sinistrinha-probability
```

## Cálculo do RTP

O RTP teórico é calculado pela soma ponderada:

```
RTP = Σ (P(combinação) × multiplicador × ratio_match) / aposta
```

O sistema garante convergência ao target (87%) através do `HouseEdgeController`, que ajusta dinamicamente os pesos das roletas em tempo real. Testes Monte Carlo com 50.000 spins confirmam que o RTP empírico permanece dentro das margens esperadas.
