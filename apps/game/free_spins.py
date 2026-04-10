"""
free_spins.py — Free spin management.

Free spins are granted by level-ups, scatter symbols (3+ bananas),
and promotions. They have a fixed bet amount and 24h expiry.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, Optional

from django.db import transaction
from django.utils import timezone


class FreeSpinSystem:
    """Manages free spin lifecycle: grant, consume, query."""

    def grant_free_spins(
        self,
        user_profile,
        count: int,
        bet_amount: Decimal,
        source: str = "level_up",
    ) -> int:
        """
        Grant free spins to a user.

        Args:
            user_profile: UserProfile model instance
            count: Number of free spins to grant
            bet_amount: Fixed bet amount for these free spins
            source: Origin of the free spins (level_up, scatter, promo)

        Returns:
            Number of free spins created
        """
        from .models import FreeSpin

        spins_created = []
        for _ in range(count):
            spins_created.append(FreeSpin(
                user=user_profile,
                bet_amount=bet_amount,
                source=source,
            ))

        FreeSpin.objects.bulk_create(spins_created)
        return count

    def use_free_spin(self, user_profile) -> Optional[Dict]:
        """
        Consume one available free spin for the user.

        Returns:
            Dict with free spin info if available, None if no free spins left.
        """
        from .models import FreeSpin

        now = timezone.now()

        with transaction.atomic():
            free_spin = (
                FreeSpin.objects
                .select_for_update()
                .filter(
                    user=user_profile,
                    is_used=False,
                    expires_at__gt=now,
                )
                .order_by("granted_at")
                .first()
            )

            if free_spin is None:
                return None

            free_spin.is_used = True
            free_spin.used_at = now
            free_spin.save(update_fields=["is_used", "used_at"])

        return {
            "free_spin_id": free_spin.id,
            "bet_amount": float(free_spin.bet_amount),
            "source": free_spin.source,
        }

    def get_remaining(self, user_profile) -> int:
        """Return count of available (unused, unexpired) free spins."""
        from .models import FreeSpin

        now = timezone.now()
        return FreeSpin.objects.filter(
            user=user_profile,
            is_used=False,
            expires_at__gt=now,
        ).count()

    def get_free_spin_info(self, user_profile) -> Dict:
        """Return detailed info about the user's free spins."""
        from .models import FreeSpin

        now = timezone.now()
        available = FreeSpin.objects.filter(
            user=user_profile,
            is_used=False,
            expires_at__gt=now,
        )

        total_available = available.count()
        next_expiry = None
        if total_available > 0:
            earliest = available.order_by("expires_at").first()
            if earliest:
                next_expiry = earliest.expires_at.isoformat()

        return {
            "available": total_available,
            "next_expiry": next_expiry,
            "total_used": FreeSpin.objects.filter(
                user=user_profile, is_used=True
            ).count(),
        }
