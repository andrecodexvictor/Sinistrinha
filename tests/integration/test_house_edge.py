"""
test_house_edge.py — Statistical tests for house edge validation.

Runs large numbers of spins against the probability engine directly
(not through Django) to validate RTP and near-miss distributions.
"""

import pytest
import time

from probability_engine.config import DEFAULT_TARGET_RTP, SYMBOLS
from probability_engine.house_edge import HouseEdgeController
from probability_engine.learning_agent import AdaptiveLearningAgent
from probability_engine.payout_calculator import PayoutCalculator
from probability_engine.weight_engine import WeightEngine


def _run_simulation(
    n_spins: int = 10_000,
    bet: float = 10.0,
    user_id: str = "test_integration",
    user_level: int = 5,
    seed: int = 42,
) -> dict:
    """Run N spins and collect aggregate statistics."""
    engine = WeightEngine(seed=seed)
    calc = PayoutCalculator()
    edge = HouseEdgeController(target_rtp=DEFAULT_TARGET_RTP)
    agent = AdaptiveLearningAgent()

    total_wagered = 0.0
    total_won = 0.0
    wins = 0
    jackpots = 0
    near_misses = 0
    combinations = {}

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

        combo = result["combination_type"]
        combinations[combo] = combinations.get(combo, 0) + 1

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
        "near_miss_rate": near_misses / n_spins,
        "combinations": combinations,
    }


class TestHouseEdge:
    """Statistical tests for house edge and RTP."""

    def test_rtp_within_range_10k_spins(self):
        """RTP should be between 60% and 110% over 10,000 spins."""
        stats = _run_simulation(n_spins=10_000, seed=42)
        assert 0.60 <= stats["rtp"] <= 1.10, (
            f"RTP {stats['rtp']:.4f} outside acceptable range [0.60, 1.10]"
        )

    def test_rtp_convergence_50k_spins(self):
        """RTP should converge closer to target over 50,000 spins."""
        stats = _run_simulation(n_spins=50_000, seed=123)
        assert 0.70 <= stats["rtp"] <= 1.05, (
            f"RTP {stats['rtp']:.4f} outside convergence range [0.70, 1.05]"
        )

    def test_house_profits_across_seeds(self):
        """House should profit in majority of simulation runs."""
        seeds = [1, 7, 13, 42, 99, 200, 314, 555, 777, 999]
        profitable = 0
        for seed in seeds:
            stats = _run_simulation(n_spins=10_000, seed=seed)
            if stats["rtp"] < 1.0:
                profitable += 1

        assert profitable >= 7, (
            f"House only profited in {profitable}/10 runs"
        )

    def test_near_miss_rate_reasonable(self):
        """Near misses should represent a reasonable proportion of spins."""
        stats = _run_simulation(n_spins=10_000, seed=42)
        # Near miss rate should be between 0% and 30%
        assert stats["near_miss_rate"] <= 0.30, (
            f"Near miss rate {stats['near_miss_rate']:.2%} is too high"
        )

    def test_win_rate_not_too_high(self):
        """Win rate should not exceed 50%"""
        stats = _run_simulation(n_spins=10_000, seed=42)
        assert stats["win_rate"] < 0.50, (
            f"Win rate {stats['win_rate']:.2%} is suspiciously high"
        )

    def test_symbol_distribution(self):
        """Verify symbol distribution is reasonable over many spins."""
        engine = WeightEngine(seed=42)
        symbol_counts = {name: 0 for name in SYMBOLS}

        n = 10_000
        for _ in range(n):
            reels = engine.spin_all(modifier=1.0)
            for sym in reels:
                symbol_counts[sym] += 1

        total = sum(symbol_counts.values())

        # Common symbols (weight >= 25) should appear frequently
        for name, sym in SYMBOLS.items():
            freq = symbol_counts[name] / total
            if sym.weight >= 25:
                assert freq > 0.10, (
                    f"Common symbol '{name}' appeared only {freq:.2%}"
                )
            elif sym.weight <= 5:
                assert freq < 0.10, (
                    f"Rare symbol '{name}' appeared too often: {freq:.2%}"
                )
