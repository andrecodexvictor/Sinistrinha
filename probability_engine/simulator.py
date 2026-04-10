"""
simulator.py — Recent Wins feed generator.

Produces a mixed feed of **real** and **simulated** wins to be displayed
at the top of the game page, creating FOMO (Fear Of Missing Out) and
social proof that others are winning.
"""

from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional

from .config import SYMBOLS, SYMBOL_NAMES


# ---------------------------------------------------------------------------
# Brazilian first names / nicknames for fake wins
# ---------------------------------------------------------------------------

_FAKE_NAMES = [
    "Lucas_TI", "Ana_Dev", "Carlos_Ops", "Bruna_DB", "Pedro_Net",
    "Julia42", "Rafael_SRE", "Mariana_QA", "Gustavo_K8s", "Fernanda_API",
    "Matheus_ML", "Larissa_UX", "Diego_SEC", "Camila_Cloud", "Thiago_DBA",
    "Bianca_PY", "Henrique_GO", "Amanda_JS", "Leandro_RPA", "Isabela_AI",
]

# Cities for geo‑proximity simulation
_FAKE_CITIES = [
    "São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba",
    "Porto Alegre", "Salvador", "Brasília", "Recife", "Fortaleza",
    "Florianópolis", "Goiânia", "Manaus", "Belém", "Campinas",
]


class RecentWinsSimulator:
    """Generates a stream of recent win entries (real + simulated)."""

    def __init__(self):
        self.real_wins: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Register a *real* win (called by the spin endpoint)
    # ------------------------------------------------------------------

    def register_real_win(
        self,
        user_id: str,
        display_name: str,
        symbol: str,
        payout: float,
        bet: float,
    ) -> None:
        entry = {
            "type": "real",
            "user": display_name,
            "symbol": symbol,
            "symbol_icon": SYMBOLS[symbol].icon if symbol in SYMBOLS else "❓",
            "payout": payout,
            "bet": bet,
            "multiplier": round(payout / bet, 2) if bet > 0 else 0,
            "timestamp": time.time(),
        }
        self.real_wins.append(entry)
        # Keep only the last 200 real wins
        if len(self.real_wins) > 200:
            self.real_wins = self.real_wins[-200:]

    # ------------------------------------------------------------------
    # Public feed
    # ------------------------------------------------------------------

    def generate_feed(
        self, limit: int = 20, real_ratio: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        Build the public feed.

        Parameters
        ----------
        limit : int
            Max entries.
        real_ratio : float
            Proportion of real‑win entries (0.0–1.0).  The rest are
            generated to fill the feed.
        """
        real_count = min(
            int(limit * real_ratio), len(self.real_wins)
        )
        fake_count = limit - real_count

        # Sample recent real wins
        reals = []
        if real_count > 0 and self.real_wins:
            pool = self.real_wins[-50:]  # from the 50 most recent
            reals = random.sample(pool, min(real_count, len(pool)))

        fakes = [self._generate_fake_win() for _ in range(fake_count)]

        feed = reals + fakes
        random.shuffle(feed)

        # Sort by (fake) timestamp descending so the newest appear first
        feed.sort(key=lambda e: e["timestamp"], reverse=True)
        return feed[:limit]

    # ------------------------------------------------------------------
    # Fake win generator
    # ------------------------------------------------------------------

    def _generate_fake_win(self) -> Dict[str, Any]:
        """Create a plausible simulated win entry."""
        # Pick a random symbol weighted towards the more "exciting" ones
        exciting = [
            n for n, s in SYMBOLS.items()
            if not s.is_wild and not s.is_scatter and s.payout_multiplier >= 5
        ]
        symbol = random.choice(exciting)
        sym = SYMBOLS[symbol]

        bet = round(random.choice([1, 2, 5, 10, 20, 25, 50]), 2)
        # Random match count biased towards 3
        match = random.choices([3, 4, 5], weights=[0.65, 0.25, 0.10], k=1)[0]
        from .config import MATCH_RATIOS
        multiplier = sym.payout_multiplier * MATCH_RATIOS[match]
        payout = round(bet * multiplier, 2)

        return {
            "type": "simulated",
            "user": random.choice(_FAKE_NAMES),
            "city": random.choice(_FAKE_CITIES),
            "symbol": symbol,
            "symbol_icon": sym.icon,
            "payout": payout,
            "bet": bet,
            "multiplier": round(multiplier, 2),
            "formatted_payout": f"R$ {payout:,.2f} em {symbol.upper().replace('_', ' ')}",
            "timestamp": time.time() - random.uniform(5, 300),
        }
