"""
house_edge.py — Dynamic RTP controller.

Ensures the house maintains its statistical advantage over time while keeping
individual sessions unpredictable enough to sustain engagement.

Key techniques
--------------
1. **RTP Targeting** – adjusts spin modifier so that the empirical RTP
   converges to a configurable target (per user level).
2. **Streak Detection** – detects consecutive wins and progressively
   tightens the modifier.
3. **Near‑Miss Generation** – when a spin would organically produce a
   jackpot, it may be downgraded to a "near miss" (the center reel is
   swapped to an adjacent symbol) with configurable probability.
4. **Volatility Cycling** – alternates between *hot*, *normal*, and *cold*
   phases to create emotional highs and lows.
5. **Session Budget Monitoring** – tracks how much of the player's budget
   has been spent and eases RTP if the player is close to churning.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from .config import (
    DEFAULT_TARGET_RTP,
    NEAR_MISS_BASE_CHANCE,
    RTP_BY_LEVEL,
    SESSION_LOSS_HARD_LIMIT,
    SESSION_LOSS_SOFT_LIMIT,
    SYMBOLS,
    SYMBOL_NAMES,
    VOLATILITY_CYCLE,
)


# ---------------------------------------------------------------------------
# Session tracking
# ---------------------------------------------------------------------------

@dataclass
class SessionStats:
    """Mutable state kept per player session."""
    user_id: str
    total_wagered: float = 0.0
    total_won: float = 0.0
    spins: int = 0
    wins: int = 0
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    initial_budget: float = 0.0
    # Volatility cycle
    volatility_mode: str = "normal"          # "hot" | "normal" | "cold"
    volatility_spins_remaining: int = 0
    # Timestamps
    session_start: float = field(default_factory=time.time)
    last_spin_ts: float = field(default_factory=time.time)

    @property
    def session_rtp(self) -> float:
        if self.total_wagered == 0:
            return 0.0
        return self.total_won / self.total_wagered

    @property
    def budget_spent_ratio(self) -> float:
        if self.initial_budget <= 0:
            return 0.0
        return (self.total_wagered - self.total_won) / self.initial_budget


class HouseEdgeController:
    """Dynamic house‑edge manager."""

    def __init__(self, target_rtp: float = DEFAULT_TARGET_RTP):
        self.target_rtp = target_rtp
        self.sessions: Dict[str, SessionStats] = {}  # user_id → stats
        self.rng = np.random.default_rng()

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def get_or_create_session(
        self, user_id: str, initial_budget: float = 0.0
    ) -> SessionStats:
        if user_id not in self.sessions:
            self.sessions[user_id] = SessionStats(
                user_id=user_id, initial_budget=initial_budget
            )
        return self.sessions[user_id]

    def reset_session(self, user_id: str) -> None:
        self.sessions.pop(user_id, None)

    # ------------------------------------------------------------------
    # Core modifier calculation
    # ------------------------------------------------------------------

    def get_spin_modifier(
        self,
        user_id: str,
        user_level: int = 1,
        user_stats: Optional[Dict] = None,
    ) -> Tuple[float, Dict[str, str]]:
        """
        Return a weight modifier (0.5 – 1.5) for the upcoming spin
        together with a reasoning dict for observability logging.

        A modifier >1 loosens reel weights (player‑friendly);
        <1 tightens them (house‑friendly).
        """
        session = self.get_or_create_session(user_id)
        reasons: Dict[str, str] = {}
        modifier = 1.0

        # --- 1. RTP convergence ---
        level_rtp = RTP_BY_LEVEL.get(user_level, self.target_rtp)
        if session.spins >= 5:
            rtp_delta = session.session_rtp - level_rtp
            # If player is winning too much → tighten
            if rtp_delta > 0.05:
                adj = max(-0.25, -rtp_delta * 2)
                modifier += adj
                reasons["rtp_convergence"] = (
                    f"session_rtp={session.session_rtp:.3f} > target={level_rtp:.3f}, "
                    f"adj={adj:+.3f}"
                )
            # If player is losing too much → ease slightly
            elif rtp_delta < -0.10:
                adj = min(0.15, abs(rtp_delta))
                modifier += adj
                reasons["rtp_convergence"] = (
                    f"session_rtp={session.session_rtp:.3f} < target={level_rtp:.3f}, "
                    f"adj={adj:+.3f}"
                )

        # --- 2. Streak detection ---
        if session.consecutive_wins >= 3:
            streak_adj = -0.05 * (session.consecutive_wins - 2)
            streak_adj = max(streak_adj, -0.20)
            modifier += streak_adj
            reasons["streak_detection"] = (
                f"{session.consecutive_wins} consecutive wins → adj={streak_adj:+.3f}"
            )
        elif session.consecutive_losses >= 5:
            loss_adj = 0.03 * (session.consecutive_losses - 4)
            loss_adj = min(loss_adj, 0.15)
            modifier += loss_adj
            reasons["streak_detection"] = (
                f"{session.consecutive_losses} consecutive losses → adj={loss_adj:+.3f}"
            )

        # --- 3. Volatility cycle ---
        self._advance_volatility(session)
        vol_adj = {"hot": 0.10, "normal": 0.0, "cold": -0.08}.get(
            session.volatility_mode, 0.0
        )
        modifier += vol_adj
        if vol_adj != 0:
            reasons["volatility"] = (
                f"mode={session.volatility_mode}, adj={vol_adj:+.3f}"
            )

        # --- 4. Session budget protection ---
        if session.initial_budget > 0:
            ratio = session.budget_spent_ratio
            if ratio >= SESSION_LOSS_HARD_LIMIT:
                modifier += 0.12
                reasons["session_budget"] = (
                    f"spent {ratio:.0%} of budget (hard limit) → +0.12"
                )
            elif ratio >= SESSION_LOSS_SOFT_LIMIT:
                modifier += 0.06
                reasons["session_budget"] = (
                    f"spent {ratio:.0%} of budget (soft limit) → +0.06"
                )

        # --- 5. Gaussian noise injection (variance) ---
        noise = float(self.rng.normal(0, 0.03))
        modifier += noise
        reasons["noise"] = f"gaussian noise {noise:+.4f}"

        # Clamp
        modifier = float(np.clip(modifier, 0.5, 1.5))
        reasons["final_modifier"] = f"{modifier:.4f}"

        return modifier, reasons

    # ------------------------------------------------------------------
    # Near‑miss handling
    # ------------------------------------------------------------------

    def should_force_near_miss(self, reels: List[str]) -> Tuple[bool, List[str]]:
        """
        Decide whether to degrade a "too good" result into a near miss.

        Returns (was_modified, resulting_reels).
        """
        # Count matches from the left
        anchor = None
        matches = 0
        for sym_name in reels:
            sym = SYMBOLS[sym_name]
            if sym.is_scatter or sym.is_wild:
                continue
            if anchor is None:
                anchor = sym_name
                matches = 1
            elif sym_name == anchor:
                matches += 1
            else:
                break

        if matches < 4:
            # Not threatening enough to warrant intervention
            return False, reels

        # Roll for near‑miss trigger
        chance = NEAR_MISS_BASE_CHANCE
        if matches == 5:
            chance *= 2.5  # much more aggressive for jackpot prevention
        if random.random() > chance:
            return False, reels

        # Degrade: swap the center reel (index 2) to a "neighbouring" symbol
        modified = list(reels)
        modified[2] = self._adjacent_symbol(anchor)
        return True, modified

    @staticmethod
    def _adjacent_symbol(symbol_name: str) -> str:
        """Pick a symbol that is 'visually close' on the reel strip."""
        idx = SYMBOL_NAMES.index(symbol_name)
        # Pick the next or previous symbol in the master list
        offset = random.choice([-1, 1])
        adj_idx = (idx + offset) % len(SYMBOL_NAMES)
        candidate = SYMBOL_NAMES[adj_idx]
        # Avoid returning wild/scatter as the near‑miss replacement
        sym = SYMBOLS[candidate]
        if sym.is_wild or sym.is_scatter:
            adj_idx = (idx + 2) % len(SYMBOL_NAMES)
            candidate = SYMBOL_NAMES[adj_idx]
        return candidate

    # ------------------------------------------------------------------
    # Session stat updates
    # ------------------------------------------------------------------

    def update_session_stats(
        self, user_id: str, bet: float, payout: float
    ) -> None:
        session = self.get_or_create_session(user_id)
        session.total_wagered += bet
        session.total_won += payout
        session.spins += 1
        session.last_spin_ts = time.time()

        if payout > 0:
            session.wins += 1
            session.consecutive_wins += 1
            session.consecutive_losses = 0
        else:
            session.consecutive_wins = 0
            session.consecutive_losses += 1

    def get_session_rtp(self, user_id: str) -> float:
        session = self.sessions.get(user_id)
        return session.session_rtp if session else 0.0

    # ------------------------------------------------------------------
    # Volatility cycling (internal)
    # ------------------------------------------------------------------

    def _advance_volatility(self, session: SessionStats) -> None:
        """Advance or transition the volatility cycle."""
        if session.volatility_spins_remaining > 0:
            session.volatility_spins_remaining -= 1
            return

        # Transition to a new mode
        modes = ["cold", "normal", "hot"]
        weights = [0.30, 0.50, 0.20]
        new_mode = random.choices(modes, weights=weights, k=1)[0]
        lo, hi = VOLATILITY_CYCLE[new_mode]
        session.volatility_mode = new_mode
        session.volatility_spins_remaining = random.randint(lo, hi)
