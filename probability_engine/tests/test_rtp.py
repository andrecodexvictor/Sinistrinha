"""
test_rtp.py — Monte Carlo simulation to validate the probability engine.

Runs thousands of spins and asserts that the empirical RTP stays within
acceptable bounds of the target (87 % ± tolerance).
"""

from __future__ import annotations

import time

import pytest

from probability_engine.config import DEFAULT_TARGET_RTP, SYMBOLS
from probability_engine.house_edge import HouseEdgeController
from probability_engine.learning_agent import AdaptiveLearningAgent
from probability_engine.payout_calculator import PayoutCalculator
from probability_engine.weight_engine import WeightEngine


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_simulation(
    n_spins: int = 10_000,
    bet: float = 10.0,
    user_id: str = "test_user",
    user_level: int = 5,
    seed: int = 42,
) -> dict:
    """Run n_spins and return aggregate statistics."""
    engine = WeightEngine(seed=seed)
    calc = PayoutCalculator()
    edge = HouseEdgeController(target_rtp=DEFAULT_TARGET_RTP)
    agent = AdaptiveLearningAgent()

    total_wagered = 0.0
    total_won = 0.0
    wins = 0
    jackpots = 0
    near_misses = 0

    for i in range(n_spins):
        modifier, _ = edge.get_spin_modifier(user_id, user_level)
        rec = agent.recommend_modifier(user_id)
        modifier += rec["weight_modifier"]
        modifier = max(0.5, min(1.5, modifier))

        reels = engine.spin_all(modifier=modifier)
        forced, reels = edge.should_force_near_miss(reels)
        result = calc.calculate(reels, bet)

        edge.update_session_stats(user_id, bet, result["payout"])
        agent.update_user_profile(user_id, {
            "bet": bet,
            "payout": result["payout"],
            "is_jackpot": result["is_jackpot"],
            "timestamp": time.time(),
        })

        total_wagered += bet
        total_won += result["payout"]
        if result["payout"] > 0:
            wins += 1
        if result["is_jackpot"]:
            jackpots += 1
        if forced:
            near_misses += 1

    rtp = total_won / total_wagered if total_wagered > 0 else 0
    return {
        "n_spins": n_spins,
        "total_wagered": total_wagered,
        "total_won": total_won,
        "rtp": rtp,
        "win_count": wins,
        "win_rate": wins / n_spins,
        "jackpots": jackpots,
        "near_misses": near_misses,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestRTP:
    """Validate RTP stays within acceptable bounds."""

    def test_rtp_within_bounds_10k_spins(self):
        """Empirical RTP should be between 60 % and 110 % over 10 000 spins."""
        stats = _run_simulation(n_spins=10_000, seed=42)
        print(f"\n[10k] RTP = {stats['rtp']:.4f} | wins = {stats['win_count']} "
              f"| jackpots = {stats['jackpots']} | near_misses = {stats['near_misses']}")
        # Wide tolerance for 10k due to variance
        assert 0.60 <= stats["rtp"] <= 1.10, (
            f"RTP {stats['rtp']:.4f} outside [0.60, 1.10]"
        )

    def test_rtp_convergence_50k_spins(self):
        """With 50 000 spins the RTP should converge closer to target."""
        stats = _run_simulation(n_spins=50_000, seed=123)
        print(f"\n[50k] RTP = {stats['rtp']:.4f} | wins = {stats['win_count']} "
              f"| jackpots = {stats['jackpots']} | near_misses = {stats['near_misses']}")
        # Tighter tolerance
        assert 0.70 <= stats["rtp"] <= 1.05, (
            f"RTP {stats['rtp']:.4f} outside [0.70, 1.05]"
        )

    def test_house_always_profits_long_run(self):
        """House must have net profit over multiple seeds."""
        seeds = [1, 7, 13, 42, 99, 200, 314, 555, 777, 999]
        profits = 0
        for seed in seeds:
            stats = _run_simulation(n_spins=10_000, seed=seed)
            if stats["rtp"] < 1.0:
                profits += 1
        # The house should profit in at least 7/10 runs
        assert profits >= 7, (
            f"House only profited in {profits}/10 runs — edge too weak"
        )


class TestPayoutCalculator:
    """Unit tests for payout logic."""

    def setup_method(self):
        self.calc = PayoutCalculator()

    def test_five_of_a_kind_jackpot(self):
        result = self.calc.calculate(["cpu"] * 5, bet=10)
        assert result["is_jackpot"] is True
        assert result["match_count"] == 5
        assert result["payout"] > 0

    def test_three_of_a_kind(self):
        result = self.calc.calculate(
            ["mouse", "mouse", "mouse", "ram", "ssd"], bet=10
        )
        assert result["match_count"] == 3
        assert result["combination_type"].startswith("3x mouse")

    def test_no_match(self):
        result = self.calc.calculate(
            ["pendrive", "mouse", "teclado", "ram", "ssd"], bet=10
        )
        assert result["payout"] == 0
        assert result["combination_type"] == "loss"

    def test_wild_completes_combo(self):
        result = self.calc.calculate(
            ["ram", "ram", "wild_sinistrinha", "ram", "ssd"], bet=10
        )
        assert result["wild_used"] is True
        # Wild at position 2 extends the chain: ram, ram, wild(=ram) → 3 match
        assert result["match_count"] >= 3

    def test_scatter_free_spins(self):
        result = self.calc.calculate(
            ["scatter_banana", "pendrive", "scatter_banana", "mouse", "scatter_banana"],
            bet=10,
        )
        assert result["free_spins"] == 5  # 3 scatters → 5 free spins

    def test_all_wilds_no_payout(self):
        """Wilds alone don't pay — they only complete combos."""
        result = self.calc.calculate(["wild_sinistrinha"] * 5, bet=10)
        assert result["payout"] == 0


class TestWeightEngine:
    """Unit tests for reel generation."""

    def test_strip_probabilities_sum_to_one(self):
        engine = WeightEngine(seed=0)
        for reel_idx in range(5):
            probs = engine.get_strip_probabilities(reel_idx)
            total = sum(probs.values())
            assert abs(total - 1.0) < 1e-9

    def test_spin_returns_valid_symbol(self):
        engine = WeightEngine(seed=0)
        for _ in range(100):
            reels = engine.spin_all()
            assert len(reels) == 5
            for sym in reels:
                assert sym in SYMBOLS

    def test_modifier_affects_distribution(self):
        """A high modifier should produce more rare symbols than a low one."""
        engine_high = WeightEngine(seed=42)
        engine_low = WeightEngine(seed=42)

        rare_high = 0
        rare_low = 0
        n = 5000
        for _ in range(n):
            for sym in engine_high.spin_all(modifier=1.4):
                if SYMBOLS[sym].weight <= 8:
                    rare_high += 1
            for sym in engine_low.spin_all(modifier=0.6):
                if SYMBOLS[sym].weight <= 8:
                    rare_low += 1

        assert rare_high > rare_low, (
            f"High modifier produced {rare_high} rares vs {rare_low} for low"
        )


class TestHouseEdgeController:
    """Unit tests for edge controller."""

    def test_modifier_within_bounds(self):
        ctrl = HouseEdgeController()
        for _ in range(50):
            mod, _ = ctrl.get_spin_modifier("u1", user_level=5)
            assert 0.5 <= mod <= 1.5

    def test_near_miss_does_not_crash(self):
        ctrl = HouseEdgeController()
        # 5-of-a-kind should sometimes trigger near miss
        reels = ["cpu", "cpu", "cpu", "cpu", "cpu"]
        forced, result = ctrl.should_force_near_miss(reels)
        assert len(result) == 5
        # If forced, center reel should be different
        if forced:
            assert result[2] != "cpu"
