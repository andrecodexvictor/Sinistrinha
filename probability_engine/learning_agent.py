"""
learning_agent.py — Adaptive behavioural profiling and recommendation engine.

Observes player actions over time and builds a lightweight profile that the
HouseEdgeController uses to fine‑tune its modifier.  No heavy ML framework
is needed; the model is a heuristic state machine augmented with simple
exponentially‑weighted moving averages (EWMA).

Psychological concepts implemented
-----------------------------------
- **Variable Ratio Reinforcement Schedule** – rewards are spaced
  unpredictably, which behavioural science shows is the most engaging
  pattern.
- **Loss Aversion Exploitation** – the system recognises when a player
  has "invested" enough to be reluctant to stop and may ease rewards
  to extend the session.
- **Near‑Miss Effect** – forwarded to the HouseEdgeController.
- **Escalation of Commitment** – detected when the player raises bets
  after consecutive losses.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# User behavioural profile
# ---------------------------------------------------------------------------

@dataclass
class UserProfile:
    """Lightweight behavioural profile for one player."""
    user_id: str
    # Betting behaviour (EWMA)
    avg_bet: float = 0.0
    bet_ewma_alpha: float = 0.15
    bet_history: List[float] = field(default_factory=list)
    # Escalation
    bet_escalation_score: float = 0.0  # 0 → 1
    # Session timing
    session_count: int = 0
    total_spins: int = 0
    total_time_seconds: float = 0.0
    last_spin_ts: float = field(default_factory=time.time)
    # Churn risk (0 = safe, 1 = about to leave)
    churn_risk: float = 0.0
    # Spin velocity (spins / minute)
    spin_velocity: float = 0.0
    _recent_spin_timestamps: List[float] = field(default_factory=list)
    # Classification
    player_type: str = "unknown"  # high_roller | cautious | grinder | whale
    # Active psychological triggers
    active_triggers: List[str] = field(default_factory=list)
    # Global cumulative stats
    lifetime_wagered: float = 0.0
    lifetime_won: float = 0.0

    @property
    def lifetime_rtp(self) -> float:
        if self.lifetime_wagered == 0:
            return 0.0
        return self.lifetime_won / self.lifetime_wagered


class AdaptiveLearningAgent:
    """Observes player behaviour and outputs modifier recommendations."""

    def __init__(self):
        self.user_profiles: Dict[str, UserProfile] = {}
        self.global_stats = {
            "total_wagered": 0.0,
            "total_paid": 0.0,
            "total_spins": 0,
        }

    # ------------------------------------------------------------------
    # Profile management
    # ------------------------------------------------------------------

    def _get_or_create(self, user_id: str) -> UserProfile:
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        return self.user_profiles[user_id]

    # ------------------------------------------------------------------
    # Update on every spin
    # ------------------------------------------------------------------

    def update_user_profile(self, user_id: str, spin_data: Dict[str, Any]) -> None:
        """
        Call after every spin with::

            spin_data = {
                "bet": float,
                "payout": float,
                "is_jackpot": bool,
                "timestamp": float,          # time.time()
            }
        """
        profile = self._get_or_create(user_id)
        bet = spin_data.get("bet", 0.0)
        payout = spin_data.get("payout", 0.0)
        ts = spin_data.get("timestamp", time.time())

        # 1. Betting EWMA
        alpha = profile.bet_ewma_alpha
        profile.avg_bet = alpha * bet + (1 - alpha) * profile.avg_bet
        profile.bet_history.append(bet)
        if len(profile.bet_history) > 100:
            profile.bet_history = profile.bet_history[-100:]

        # 2. Bet escalation detection
        if len(profile.bet_history) >= 3:
            recent = profile.bet_history[-3:]
            if recent[-1] > recent[-2] > recent[-3]:
                profile.bet_escalation_score = min(
                    1.0, profile.bet_escalation_score + 0.15
                )
            else:
                profile.bet_escalation_score = max(
                    0.0, profile.bet_escalation_score - 0.05
                )

        # 3. Spin velocity
        profile._recent_spin_timestamps.append(ts)
        if len(profile._recent_spin_timestamps) > 20:
            profile._recent_spin_timestamps = profile._recent_spin_timestamps[-20:]
        if len(profile._recent_spin_timestamps) >= 2:
            span = (
                profile._recent_spin_timestamps[-1]
                - profile._recent_spin_timestamps[0]
            )
            if span > 0:
                profile.spin_velocity = (
                    (len(profile._recent_spin_timestamps) - 1) / span * 60
                )

        # 4. Churn risk heuristic
        profile.churn_risk = self._estimate_churn(profile, payout)

        # 5. Player classification
        profile.player_type = self._classify(profile)

        # 6. Active triggers
        profile.active_triggers = self._detect_triggers(profile, payout)

        # 7. Lifetime accumulators
        profile.total_spins += 1
        profile.lifetime_wagered += bet
        profile.lifetime_won += payout
        profile.last_spin_ts = ts

        # Global
        self.global_stats["total_wagered"] += bet
        self.global_stats["total_paid"] += payout
        self.global_stats["total_spins"] += 1

    # ------------------------------------------------------------------
    # Recommendation
    # ------------------------------------------------------------------

    def recommend_modifier(self, user_id: str) -> Dict[str, Any]:
        """
        Suggest modifier adjustments for the next spin.

        The HouseEdgeController should *add* these values on top of its
        own calculations.
        """
        profile = self._get_or_create(user_id)
        weight_mod = 0.0
        near_miss_prob = 0.15  # base
        bonus_trigger = 0.02  # 2 % base
        reasoning_parts: List[str] = []

        # High churn risk → loosen slightly
        if profile.churn_risk > 0.7:
            weight_mod += 0.08
            bonus_trigger += 0.03
            reasoning_parts.append(
                f"High churn risk ({profile.churn_risk:.2f}) → loosening"
            )

        # Escalation of commitment detected → keep engagement
        if profile.bet_escalation_score > 0.5:
            near_miss_prob += 0.10
            reasoning_parts.append(
                f"Bet escalation ({profile.bet_escalation_score:.2f}) → more near‑misses"
            )

        # Whale / high roller → slightly tighten (they can afford it)
        if profile.player_type == "whale":
            weight_mod -= 0.05
            reasoning_parts.append("Whale detected → slight tightening")
        elif profile.player_type == "cautious":
            weight_mod += 0.04
            reasoning_parts.append("Cautious player → slight loosening")

        # Variable ratio schedule: inject random bonus chance
        if profile.total_spins > 0 and profile.total_spins % 17 == 0:
            bonus_trigger += 0.05
            reasoning_parts.append("Variable ratio trigger (spin mod 17)")

        return {
            "weight_modifier": round(weight_mod, 4),
            "near_miss_probability": round(min(near_miss_prob, 0.50), 4),
            "bonus_trigger_chance": round(min(bonus_trigger, 0.15), 4),
            "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "baseline",
        }

    # ------------------------------------------------------------------
    # Behavioural report (admin / debug)
    # ------------------------------------------------------------------

    def export_behavioral_report(self, user_id: str) -> Dict[str, Any]:
        profile = self._get_or_create(user_id)
        return {
            "user_id": profile.user_id,
            "player_type": profile.player_type,
            "avg_bet": round(profile.avg_bet, 2),
            "bet_escalation_score": round(profile.bet_escalation_score, 3),
            "spin_velocity_per_min": round(profile.spin_velocity, 2),
            "churn_risk": round(profile.churn_risk, 3),
            "total_spins": profile.total_spins,
            "lifetime_wagered": round(profile.lifetime_wagered, 2),
            "lifetime_won": round(profile.lifetime_won, 2),
            "lifetime_rtp": round(profile.lifetime_rtp, 4),
            "active_triggers": profile.active_triggers,
            "session_count": profile.session_count,
        }

    # ------------------------------------------------------------------
    # Internal heuristics
    # ------------------------------------------------------------------

    @staticmethod
    def _estimate_churn(profile: UserProfile, last_payout: float) -> float:
        """Simple churn heuristic based on losing rate and slowing velocity."""
        risk = profile.churn_risk

        # Losing money fast increases risk
        if profile.lifetime_wagered > 0:
            loss_ratio = 1 - profile.lifetime_rtp
            if loss_ratio > 0.25:
                risk += 0.04
            elif loss_ratio > 0.15:
                risk += 0.02

        # Slowing spin rate implies disengagement
        if profile.spin_velocity < 5 and profile.total_spins > 10:
            risk += 0.03

        # Recent win decreases risk
        if last_payout > 0:
            risk -= 0.06

        return float(max(0.0, min(1.0, risk)))

    @staticmethod
    def _classify(profile: UserProfile) -> str:
        if profile.avg_bet >= 100:
            return "whale"
        if profile.avg_bet >= 30:
            return "high_roller"
        if profile.spin_velocity >= 20:
            return "grinder"
        if profile.avg_bet <= 5:
            return "cautious"
        return "regular"

    @staticmethod
    def _detect_triggers(profile: UserProfile, last_payout: float) -> List[str]:
        triggers: List[str] = []
        if profile.bet_escalation_score > 0.4:
            triggers.append("escalation_of_commitment")
        if profile.churn_risk > 0.6:
            triggers.append("loss_aversion_exploitation")
        if profile.total_spins > 0 and profile.total_spins % 17 == 0:
            triggers.append("variable_ratio_reinforcement")
        if last_payout == 0 and profile.total_spins > 5:
            triggers.append("near_miss_effect")
        return triggers
