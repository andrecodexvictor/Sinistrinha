"""
bonus_service.py — Manages free spins, bonus multipliers, and bonus transactions.

All bonus operations create an audit-trail Transaction of type BONUS.
"""

import logging
from decimal import Decimal
from typing import Optional

from apps.payments.models import Transaction
from apps.users.models import UserProfile

logger = logging.getLogger(__name__)


class BonusService:
    """Handles free spin mechanics and bonus distribution."""

    @staticmethod
    def grant_free_spins(profile: UserProfile, count: int, reason: str = "level_up") -> None:
        """
        Grant free spins to a player and log a bonus transaction.

        Parameters
        ----------
        profile : UserProfile
            The player's profile.
        count : int
            Number of free spins to grant.
        reason : str
            Why the free spins were granted (for audit metadata).
        """
        if count <= 0:
            return

        profile.free_spins += count
        profile.save(update_fields=["free_spins"])

        # Audit trail
        Transaction.objects.create(
            user=profile,
            amount=Decimal("0.00"),  # Free spins have no direct monetary value
            transaction_type=Transaction.TransactionType.BONUS,
            status=Transaction.TransactionStatus.COMPLETED,
            metadata={
                "bonus_type": "free_spins",
                "count": count,
                "reason": reason,
            },
        )

        logger.info(
            f"Granted {count} free spins to user {profile.user_id} (reason: {reason})"
        )

    @staticmethod
    def consume_free_spin(profile: UserProfile) -> bool:
        """
        Attempt to consume one free spin.

        Returns True if a free spin was available and consumed, False otherwise.
        """
        if profile.free_spins <= 0:
            return False

        profile.free_spins -= 1
        profile.save(update_fields=["free_spins"])
        return True

    @staticmethod
    def grant_bonus_coins(
        profile: UserProfile, amount: float, reason: str = "level_up"
    ) -> None:
        """
        Grant bonus coins to a player and log a bonus transaction.

        Parameters
        ----------
        profile : UserProfile
            The player's profile.
        amount : float
            Amount of bonus coins to grant.
        reason : str
            Why the bonus was granted (for audit metadata).
        """
        if amount <= 0:
            return

        decimal_amount = Decimal(str(amount))
        profile.balance += decimal_amount
        profile.save(update_fields=["balance"])

        Transaction.objects.create(
            user=profile,
            amount=decimal_amount,
            transaction_type=Transaction.TransactionType.BONUS,
            status=Transaction.TransactionStatus.COMPLETED,
            metadata={
                "bonus_type": "bonus_coins",
                "reason": reason,
            },
        )

        logger.info(
            f"Granted {amount} bonus coins to user {profile.user_id} (reason: {reason})"
        )

    @staticmethod
    def apply_level_bonus(
        profile: UserProfile,
        bonus_coins: float,
        free_spins: int,
        level: int,
    ) -> None:
        """
        Apply all bonuses for a level-up event.
        This is called by LevelService after a level-up is confirmed.

        Creates individual audit transactions for coins and free spins.
        """
        reason = f"level_up_to_{level}"

        if bonus_coins > 0:
            BonusService.grant_bonus_coins(profile, bonus_coins, reason)

        if free_spins > 0:
            BonusService.grant_free_spins(profile, free_spins, reason)
