"""
test_bonus_service.py — Unit tests for the BonusService.
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User

from apps.users.models import UserProfile
from apps.payments.models import Transaction
from apps.game.services.bonus_service import BonusService


class BonusServiceTestCase(TestCase):
    """Tests for free spin management and bonus coin distribution."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="bonusplayer", password="testpass123"
        )
        self.profile = UserProfile.objects.create(
            user=self.user, balance=Decimal("500.00"), level=1, xp=0
        )

    def test_grant_free_spins(self):
        """Grant free spins should increment the count and create a transaction."""
        BonusService.grant_free_spins(self.profile, 5, reason="test_bonus")
        self.profile.refresh_from_db()

        self.assertEqual(self.profile.free_spins, 5)

        # Verify audit transaction
        tx = Transaction.objects.filter(
            user=self.profile,
            transaction_type=Transaction.TransactionType.BONUS,
        ).first()
        self.assertIsNotNone(tx)
        self.assertEqual(tx.metadata["bonus_type"], "free_spins")
        self.assertEqual(tx.metadata["count"], 5)

    def test_grant_zero_free_spins_is_noop(self):
        """Granting 0 free spins should not create a transaction."""
        BonusService.grant_free_spins(self.profile, 0)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_consume_free_spin_success(self):
        """Consuming a free spin when available should return True."""
        self.profile.free_spins = 3
        self.profile.save()

        result = BonusService.consume_free_spin(self.profile)
        self.profile.refresh_from_db()

        self.assertTrue(result)
        self.assertEqual(self.profile.free_spins, 2)

    def test_consume_free_spin_when_none_available(self):
        """Consuming a free spin with 0 available should return False."""
        self.profile.free_spins = 0
        self.profile.save()

        result = BonusService.consume_free_spin(self.profile)

        self.assertFalse(result)
        self.assertEqual(self.profile.free_spins, 0)

    def test_grant_bonus_coins(self):
        """Granting bonus coins should increase balance and create a transaction."""
        initial_balance = self.profile.balance
        BonusService.grant_bonus_coins(self.profile, 100.0, reason="level_up")
        self.profile.refresh_from_db()

        self.assertEqual(self.profile.balance, initial_balance + Decimal("100.00"))

        tx = Transaction.objects.filter(
            user=self.profile,
            transaction_type=Transaction.TransactionType.BONUS,
        ).first()
        self.assertIsNotNone(tx)
        self.assertEqual(tx.amount, Decimal("100.00"))
        self.assertEqual(tx.metadata["bonus_type"], "bonus_coins")

    def test_grant_zero_bonus_coins_is_noop(self):
        """Granting 0 coins should not create a transaction."""
        BonusService.grant_bonus_coins(self.profile, 0)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_apply_level_bonus(self):
        """apply_level_bonus should grant both coins and free spins."""
        BonusService.apply_level_bonus(
            self.profile, bonus_coins=200.0, free_spins=10, level=5
        )
        self.profile.refresh_from_db()

        self.assertEqual(self.profile.balance, Decimal("700.00"))  # 500 + 200
        self.assertEqual(self.profile.free_spins, 10)

        # Should have 2 transactions: one for coins, one for free spins
        txs = Transaction.objects.filter(
            user=self.profile,
            transaction_type=Transaction.TransactionType.BONUS,
        )
        self.assertEqual(txs.count(), 2)
