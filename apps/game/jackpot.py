"""
jackpot.py — Progressive jackpot system.

The jackpot pool is fed by 2% of every bet across all players.
A jackpot is won only when all 5 reels show 'gorila_dourado'.
"""

from __future__ import annotations

from decimal import Decimal
from typing import List

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

JACKPOT_CACHE_KEY = "sinistrinha:jackpot:current"
JACKPOT_CONTRIBUTION_RATE = Decimal("0.02")  # 2% of each bet
JACKPOT_MINIMUM = Decimal("500.00")          # Pool floor after reset
JACKPOT_SYMBOL = "gorila_dourado"


class JackpotSystem:
    """Progressive jackpot management."""

    def contribute(self, bet_amount: Decimal) -> Decimal:
        """
        Add 2% of the bet to the jackpot pool.
        Returns the contribution amount.
        """
        from .models import JackpotPool

        contribution = (bet_amount * JACKPOT_CONTRIBUTION_RATE).quantize(Decimal("0.01"))

        with transaction.atomic():
            pool = JackpotPool.objects.select_for_update().get(pk=1)
            pool.current_amount += contribution
            pool.save(update_fields=["current_amount"])

        # Update cache
        cache.set(JACKPOT_CACHE_KEY, float(pool.current_amount), timeout=300)
        return contribution

    @staticmethod
    def check_jackpot_win(reels: List[str]) -> bool:
        """Check if the reels result in a jackpot (5x gorila_dourado)."""
        return all(r == JACKPOT_SYMBOL for r in reels)

    def pay_jackpot(self, winner_profile) -> Decimal:
        """
        Pay the full jackpot pool to the winner and reset the pool.
        Returns the amount paid.
        """
        from .models import JackpotPool

        with transaction.atomic():
            pool = JackpotPool.objects.select_for_update().get(pk=1)
            amount = pool.current_amount

            # Credit winner
            winner_profile.balance += amount
            winner_profile.total_won += amount
            winner_profile.save(update_fields=["balance", "total_won"])

            # Reset pool
            pool.current_amount = JACKPOT_MINIMUM
            pool.last_won_by = winner_profile
            pool.last_won_at = timezone.now()
            pool.save(update_fields=["current_amount", "last_won_by", "last_won_at"])

        # Update cache
        cache.set(JACKPOT_CACHE_KEY, float(JACKPOT_MINIMUM), timeout=300)
        return amount

    def get_current_amount(self) -> float:
        """Return current jackpot amount (from cache if available)."""
        cached = cache.get(JACKPOT_CACHE_KEY)
        if cached is not None:
            return float(cached)

        from .models import JackpotPool
        try:
            pool = JackpotPool.objects.get(pk=1)
            amount = float(pool.current_amount)
            cache.set(JACKPOT_CACHE_KEY, amount, timeout=300)
            return amount
        except JackpotPool.DoesNotExist:
            return float(JACKPOT_MINIMUM)
