"""
level_service.py — Core leveling engine for the Sinistrinha game.

Handles XP awarding, level-up checks, bonus distribution on level-up,
and RTP modifier lookup based on player level.
"""

import logging
from typing import Any, Dict, Optional

from django.db import transaction

from apps.game.models import LevelConfig
from apps.users.models import UserProfile
from probability_engine.config import RTP_BY_LEVEL

logger = logging.getLogger(__name__)


class LevelUpEvent:
    """Data object describing a level-up occurrence."""

    def __init__(
        self,
        old_level: int,
        new_level: int,
        bonus_coins: float,
        free_spins: int,
        prize_name: str,
    ):
        self.old_level = old_level
        self.new_level = new_level
        self.bonus_coins = bonus_coins
        self.free_spins = free_spins
        self.prize_name = prize_name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "old_level": self.old_level,
            "new_level": self.new_level,
            "bonus_coins": float(self.bonus_coins),
            "free_spins": self.free_spins,
            "prize_name": self.prize_name,
        }


class LevelService:
    """Manages XP progression and level-up logic."""

    @staticmethod
    def award_xp(profile: UserProfile, xp_amount: int) -> Optional[LevelUpEvent]:
        """
        Add XP to a user profile and check for level-up.

        Parameters
        ----------
        profile : UserProfile
            The player's profile (must be inside an active transaction).
        xp_amount : int
            Amount of XP to award.

        Returns
        -------
        LevelUpEvent or None
            If the player leveled up, returns the event details.
        """
        profile.xp += xp_amount
        level_up_event = LevelService.check_level_up(profile)
        profile.save(update_fields=["xp", "level", "balance", "free_spins"])
        return level_up_event

    @staticmethod
    def check_level_up(profile: UserProfile) -> Optional[LevelUpEvent]:
        """
        Check whether the user has enough XP to reach the next level.
        Handles multi-level jumps (rare but possible with large XP bonuses).

        Returns a LevelUpEvent if the player leveled up, None otherwise.
        """
        cumulative_bonus_coins = 0
        cumulative_free_spins = 0
        old_level = profile.level
        latest_prize = ""

        while True:
            next_level = profile.level + 1
            try:
                config = LevelConfig.objects.get(level=next_level)
            except LevelConfig.DoesNotExist:
                # Max level reached — no more level-ups possible
                break

            if profile.xp < config.xp_required:
                break

            # Level up!
            profile.level = next_level
            cumulative_bonus_coins += float(config.bonus_coins)
            cumulative_free_spins += config.free_spins
            latest_prize = config.prize_name

            logger.info(
                f"Player {profile.user_id} leveled up to {next_level} "
                f"(bonus: {config.bonus_coins} coins, {config.free_spins} free spins)"
            )

        if profile.level > old_level:
            # Apply cumulative bonuses
            from decimal import Decimal

            profile.balance += Decimal(str(cumulative_bonus_coins))
            profile.free_spins += cumulative_free_spins

            return LevelUpEvent(
                old_level=old_level,
                new_level=profile.level,
                bonus_coins=cumulative_bonus_coins,
                free_spins=cumulative_free_spins,
                prize_name=latest_prize,
            )

        return None

    @staticmethod
    def get_current_rtp(profile: UserProfile) -> float:
        """
        Look up the RTP (Return-to-Player) for the user's current level.

        Falls back to level 1 RTP if the level is not in the table,
        and caps at the highest defined level.
        """
        level = profile.level
        if level in RTP_BY_LEVEL:
            return RTP_BY_LEVEL[level]

        # If above max level in table, use the highest RTP
        max_level = max(RTP_BY_LEVEL.keys())
        if level > max_level:
            return RTP_BY_LEVEL[max_level]

        # Use level 1 as fallback
        return RTP_BY_LEVEL.get(1, 0.85)

    @staticmethod
    def get_rtp_modifier(profile: UserProfile) -> float:
        """
        Compute a weight modifier for the probability engine based on
        the user's RTP and house_edge_modifier from their LevelConfig.

        A modifier > 1.0 makes rare symbols more likely (generous).
        """
        rtp = LevelService.get_current_rtp(profile)

        # Get house_edge_modifier from LevelConfig if it exists
        try:
            config = LevelConfig.objects.get(level=profile.level)
            house_mod = config.house_edge_modifier
        except LevelConfig.DoesNotExist:
            house_mod = 1.0

        # Convert RTP into a spin modifier
        # Base RTP = 0.85 (level 1). modifier = 1.0 at base.
        # Each 0.01 RTP above base → +0.1 modifier
        base_rtp = 0.85
        rtp_delta = rtp - base_rtp
        modifier = 1.0 + (rtp_delta * 10)  # e.g. rtp=0.895 → modifier=1.45

        return modifier * house_mod
