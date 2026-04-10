"""
weight_engine.py — Virtual reel strip management and symbol selection.

Each of the 5 reels has an independent virtual strip whose symbol distribution
can be tuned individually.  Reels 1 & 5 (the extremities) are weighted towards
common symbols, while reel 3 (center) carries slightly higher rare‑symbol
frequency to produce convincing "near miss" scenarios.
"""

from __future__ import annotations

import copy
import random
from typing import Dict, List, Optional

import numpy as np

from .config import (
    REEL_COUNT,
    SYMBOLS,
    SYMBOL_NAMES,
    TOTAL_BASE_WEIGHT,
    Symbol,
)


class WeightEngine:
    """Manages per‑reel virtual strips and performs weighted spins."""

    def __init__(self, reel_count: int = REEL_COUNT, seed: Optional[int] = None):
        self.reel_count = reel_count
        self.rng = np.random.default_rng(seed)
        # Each element is {symbol_name: adjusted_weight, …}
        self.reel_strips: List[Dict[str, float]] = self._generate_reel_strips()

    # ------------------------------------------------------------------
    # Strip generation
    # ------------------------------------------------------------------

    def _generate_reel_strips(self) -> List[Dict[str, float]]:
        """
        Build independent strips.

        Strategy:
        - Reels 0 & 4 (left‑most / right‑most) → inflate common symbols by 15 %,
          deflate rare symbols by 20 %.
        - Reel 2 (center) → inflate rare symbols by 10 % to create near‑miss
          patterns where the center *almost* completes a big win.
        - Reels 1 & 3 → keep base weights unchanged.
        """
        strips: List[Dict[str, float]] = []

        for reel_idx in range(self.reel_count):
            strip: Dict[str, float] = {}
            for name, sym in SYMBOLS.items():
                base = float(sym.weight)

                if reel_idx in (0, 4):  # extremes
                    if sym.weight >= 25:        # common
                        base *= 1.15
                    elif sym.weight <= 8:        # rare
                        base *= 0.80
                elif reel_idx == 2:              # center
                    if sym.weight <= 8:
                        base *= 1.10
                    elif sym.weight >= 25:
                        base *= 0.95

                strip[name] = base

            strips.append(strip)

        return strips

    # ------------------------------------------------------------------
    # Spinning
    # ------------------------------------------------------------------

    def spin_reel(self, reel_index: int, modifier: float = 1.0) -> str:
        """
        Spin a single reel and return the chosen symbol name.

        Parameters
        ----------
        reel_index : int
            Which reel to spin (0‑indexed).
        modifier : float
            A multiplier applied to **rare** symbol weights.
            >1 makes rare symbols more likely (generous), <1 makes them
            less likely (tight).  Common symbols are inversely adjusted
            so the total weight sum stays roughly constant.
        """
        strip = self.reel_strips[reel_index]
        names: List[str] = list(strip.keys())
        weights = np.array([strip[n] for n in names], dtype=np.float64)

        if modifier != 1.0:
            weights = self._apply_modifier(names, weights, modifier)

        # Normalise to probabilities
        probs = weights / weights.sum()
        idx = self.rng.choice(len(names), p=probs)
        return names[idx]

    def spin_all(self, modifier: float = 1.0) -> List[str]:
        """Spin all reels and return a list of symbol names."""
        return [self.spin_reel(i, modifier) for i in range(self.reel_count)]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_modifier(
        names: List[str],
        weights: np.ndarray,
        modifier: float,
    ) -> np.ndarray:
        """
        Adjust weights by inflating/deflating rare vs common symbols.

        When modifier > 1.0 rare symbols become more frequent (player
        advantage).  When modifier < 1.0, common symbols dominate.
        """
        adjusted = weights.copy()
        for i, name in enumerate(names):
            sym = SYMBOLS[name]
            if sym.weight <= 8:   # rare / ultra‑rare / special
                adjusted[i] *= modifier
            elif sym.weight >= 25:  # common
                # inverse adjustment to preserve total probability mass
                adjusted[i] *= (2.0 - modifier)

        # Floor at a small positive number to avoid zero‑probability
        adjusted = np.maximum(adjusted, 0.1)
        return adjusted

    def get_strip_probabilities(self, reel_index: int) -> Dict[str, float]:
        """Return normalised probabilities for a given reel (for debugging)."""
        strip = self.reel_strips[reel_index]
        total = sum(strip.values())
        return {name: w / total for name, w in strip.items()}
