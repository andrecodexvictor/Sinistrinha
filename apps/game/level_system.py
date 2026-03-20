"""
level_system.py — Level progression, XP calculation, and reward granting.

Each level unlocks bonus coins, free spins, and virtual IT prizes.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

LEVEL_CONFIG: List[Dict] = [
    {"level": 1,  "xp": 0,      "bonus": 5.00,    "free_spins": 3,   "prize": "Pendrive 32GB",        "icon": "🔌", "rarity": "comum"},
    {"level": 2,  "xp": 100,    "bonus": 8.00,    "free_spins": 5,   "prize": "Mouse Simples",        "icon": "🖱️", "rarity": "comum"},
    {"level": 3,  "xp": 250,    "bonus": 12.00,   "free_spins": 5,   "prize": "Mousepad Gamer",       "icon": "🎯", "rarity": "comum"},
    {"level": 5,  "xp": 600,    "bonus": 20.00,   "free_spins": 8,   "prize": "Teclado Mecânico",     "icon": "⌨️", "rarity": "incomum"},
    {"level": 8,  "xp": 1500,   "bonus": 35.00,   "free_spins": 10,  "prize": "Headset Gamer",        "icon": "🎧", "rarity": "incomum"},
    {"level": 10, "xp": 3000,   "bonus": 50.00,   "free_spins": 15,  "prize": "RAM DDR4 8GB",         "icon": "💾", "rarity": "raro"},
    {"level": 15, "xp": 7000,   "bonus": 100.00,  "free_spins": 20,  "prize": "RAM DDR5 16GB",        "icon": "💾", "rarity": "raro"},
    {"level": 20, "xp": 15000,  "bonus": 200.00,  "free_spins": 25,  "prize": "SSD NVMe 1TB",         "icon": "💿", "rarity": "raro"},
    {"level": 25, "xp": 30000,  "bonus": 350.00,  "free_spins": 30,  "prize": "Monitor 1080p 144Hz",  "icon": "🖥️", "rarity": "epico"},
    {"level": 30, "xp": 60000,  "bonus": 500.00,  "free_spins": 40,  "prize": "Monitor 4K 144Hz",     "icon": "🖥️", "rarity": "epico"},
    {"level": 35, "xp": 100000, "bonus": 750.00,  "free_spins": 50,  "prize": "Processador i9-14K",   "icon": "🔲", "rarity": "epico"},
    {"level": 40, "xp": 200000, "bonus": 1000.00, "free_spins": 75,  "prize": "RTX 4080 Super",       "icon": "🎮", "rarity": "lendario"},
    {"level": 50, "xp": 500000, "bonus": 2000.00, "free_spins": 100, "prize": "RTX 4090 + PC Gamer",  "icon": "🦍", "rarity": "lendario"},
]


class LevelSystem:
    """Handles XP calculation, level-up detection, and reward granting."""

    def __init__(self):
        # Sort config by level for ordered lookup
        self._config = sorted(LEVEL_CONFIG, key=lambda c: c["level"])

    def calculate_xp_for_spin(self, bet: float, payout: float, combination: str) -> int:
        """
        XP earned per spin:
        - Each real wagered = 1 XP base
        - Outcome multipliers: lose=1x, small_win=1.5x, medium_win=2x,
          big_win=3x, jackpot=10x, scatter_win=1.5x
        - High-bet bonus (>= R$10): +50% XP
        """
        base_xp = max(int(bet), 1)

        outcome_multipliers = {
            "lose": 1.0,
            "loss": 1.0,
            "small_win": 1.5,
            "medium_win": 2.0,
            "big_win": 3.0,
            "scatter_win": 1.5,
            "jackpot": 10.0,
        }

        # Handle combination types that come from probability engine
        # e.g., "3x mouse", "JACKPOT 5x gorila_dourado", "loss"
        combo_key = combination.lower()
        if "jackpot" in combo_key:
            multi = 10.0
        elif combo_key in outcome_multipliers:
            multi = outcome_multipliers[combo_key]
        elif payout > 0:
            ratio = payout / bet if bet > 0 else 0
            if ratio >= 10:
                multi = 3.0
            elif ratio >= 3:
                multi = 2.0
            else:
                multi = 1.5
        else:
            multi = 1.0

        xp = int(base_xp * multi)

        # High-bet bonus
        if bet >= 10.0:
            xp = int(xp * 1.5)

        return max(xp, 10)  # minimum 10 XP per spin

    def get_xp_multiplier_for_event(self, event_type: str = None) -> float:
        """
        Event-based XP multipliers (applied on top of base XP):
        - first_spin_of_day: 2x
        - weekend: 1.5x
        - jackpot_hour (21h-23h): 1.3x
        """
        now = datetime.now()
        multiplier = 1.0

        # Weekend bonus
        if now.weekday() >= 5:  # Saturday=5, Sunday=6
            multiplier *= 1.5

        # Jackpot hour (21h-23h)
        if 21 <= now.hour < 23:
            multiplier *= 1.3

        # Explicit event type
        if event_type == "first_spin_of_day":
            multiplier *= 2.0

        return multiplier

    def check_level_up(self, current_level: int, current_xp: int) -> Optional[Dict]:
        """
        Check if user qualifies for a level up.
        Returns the new level config dict if they leveled up, else None.
        """
        # Find the next level they haven't reached
        for cfg in self._config:
            if cfg["level"] > current_level and current_xp >= cfg["xp"]:
                # Check if there's an even higher level they qualify for
                best = cfg
                for higher in self._config:
                    if higher["level"] > best["level"] and current_xp >= higher["xp"]:
                        best = higher
                return best
        return None

    def grant_level_reward(self, profile, level_config: Dict) -> Dict:
        """
        Grant the reward for reaching a new level.
        Updates profile balance and returns reward details.

        Args:
            profile: UserProfile model instance
            level_config: dict from LEVEL_CONFIG

        Returns:
            dict with reward details
        """
        bonus = Decimal(str(level_config["bonus"]))
        profile.balance += bonus
        profile.level = level_config["level"]
        profile.save(update_fields=["balance", "level"])

        return {
            "new_level": level_config["level"],
            "bonus_coins": float(bonus),
            "free_spins": level_config["free_spins"],
            "prize": level_config["prize"],
            "prize_icon": level_config["icon"],
            "prize_rarity": level_config["rarity"],
        }

    def get_level_progress(self, current_level: int, current_xp: int) -> Dict:
        """Return progress info toward the next level."""
        next_level = None
        for cfg in self._config:
            if cfg["level"] > current_level:
                next_level = cfg
                break

        if next_level is None:
            return {
                "current_level": current_level,
                "current_xp": current_xp,
                "next_level": None,
                "xp_required": 0,
                "xp_remaining": 0,
                "progress_percent": 100.0,
            }

        # Find XP for current level
        current_level_xp = 0
        for cfg in self._config:
            if cfg["level"] == current_level:
                current_level_xp = cfg["xp"]
                break

        xp_in_range = current_xp - current_level_xp
        xp_needed = next_level["xp"] - current_level_xp
        progress = (xp_in_range / xp_needed * 100) if xp_needed > 0 else 100.0

        return {
            "current_level": current_level,
            "current_xp": current_xp,
            "next_level": next_level["level"],
            "xp_required": next_level["xp"],
            "xp_remaining": max(0, next_level["xp"] - current_xp),
            "progress_percent": min(100.0, round(progress, 1)),
        }
