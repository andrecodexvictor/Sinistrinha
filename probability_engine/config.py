"""
config.py — Game symbol definitions, base weights, and payout tables.

All symbols follow an IT / hardware theme. Weights determine how often a symbol
appears on a virtual reel strip; higher weight = more frequent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


# ---------------------------------------------------------------------------
# Symbol dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Symbol:
    """Immutable description of a single slot symbol."""
    name: str
    weight: int
    payout_multiplier: float
    icon: str
    is_wild: bool = False
    is_scatter: bool = False


# ---------------------------------------------------------------------------
# Master symbol table
# ---------------------------------------------------------------------------

SYMBOLS: Dict[str, Symbol] = {
    # Alta frequência (comuns, baixo pagamento)
    "pendrive":         Symbol("pendrive",         weight=35, payout_multiplier=1.5,   icon="🔌"),
    "mouse":            Symbol("mouse",            weight=30, payout_multiplier=2.0,   icon="🖱️"),
    "teclado":          Symbol("teclado",          weight=28, payout_multiplier=2.5,   icon="⌨️"),

    # Média frequência
    "ram":              Symbol("ram",              weight=18, payout_multiplier=5.0,   icon="💾"),
    "ssd":              Symbol("ssd",              weight=15, payout_multiplier=8.0,   icon="💿"),
    "monitor":          Symbol("monitor",          weight=12, payout_multiplier=12.0,  icon="🖥️"),

    # Baixa frequência (raros, alto pagamento)
    "cpu":              Symbol("cpu",              weight=8,  payout_multiplier=25.0,  icon="🔲"),
    "gpu_rtx":          Symbol("gpu_rtx",          weight=5,  payout_multiplier=50.0,  icon="🎮"),

    # Ultra‑raro
    "gorila_dourado":   Symbol("gorila_dourado",   weight=2,  payout_multiplier=150.0, icon="🦍"),

    # Wild e especiais
    "wild_sinistrinha": Symbol("wild_sinistrinha", weight=3,  payout_multiplier=0,     icon="🃏", is_wild=True),
    "scatter_banana":   Symbol("scatter_banana",   weight=4,  payout_multiplier=0,     icon="🍌", is_scatter=True),
}

# Convenience list of symbol names (order matters for deterministic iteration)
SYMBOL_NAMES: List[str] = list(SYMBOLS.keys())

# Total base weight (sum across all symbols)
TOTAL_BASE_WEIGHT: int = sum(s.weight for s in SYMBOLS.values())  # 160

# ---------------------------------------------------------------------------
# Game constants
# ---------------------------------------------------------------------------

REEL_COUNT = 5
ROWS_VISIBLE = 3  # rows visible to the player per reel

# Default target Return‑to‑Player (87 % → 13 % house edge)
DEFAULT_TARGET_RTP = 0.87

# RTP per user level (higher level → slightly more generous)
RTP_BY_LEVEL: Dict[int, float] = {
    1:  0.85,
    2:  0.855,
    3:  0.86,
    4:  0.865,
    5:  0.87,
    6:  0.875,
    7:  0.88,
    8:  0.885,
    9:  0.89,
    10: 0.895,
}

# Near‑miss probability thresholds
NEAR_MISS_BASE_CHANCE = 0.15  # 15 % chance of forcing a near miss

# Volatility cycle lengths (in number of spins)
VOLATILITY_CYCLE = {
    "cold":   (20, 50),    # cold streak lasts 20‑50 spins
    "normal": (30, 80),
    "hot":    (10, 25),    # hot streaks are shorter
}

# Session budget alert thresholds (multiplier of initial deposit)
SESSION_LOSS_SOFT_LIMIT = 0.70   # 70 % of budget lost → slightly ease RTP
SESSION_LOSS_HARD_LIMIT = 0.90   # 90 % → more aggressive easing to avoid churn

# Payout ratios for partial matches (relative to 5‑of‑a‑kind multiplier)
MATCH_RATIOS = {
    5: 1.00,
    4: 0.70,
    3: 0.40,
}
WILD_BONUS_MULTIPLIER = 1.20  # +20 % if a wild completes the combo
GLOBAL_MULTIPLIER_BOOST = 12.0 # Adjusts single-line payouts to competitive RTP

# Scatter rules
SCATTER_FREE_SPINS = {
    2: 2,   # 2 scatters → 2 free spins
    3: 5,
    4: 8,
    5: 12,
}
SCATTER_BONUS_MULTIPLIER = {
    3: 1.5,
    4: 2.0,
    5: 3.0,
}

# XP bonus per spin outcome
XP_PER_SPIN = 10
XP_WIN_BONUS = 25
XP_JACKPOT_BONUS = 500
