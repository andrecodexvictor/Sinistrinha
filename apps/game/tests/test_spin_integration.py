"""
test_spin_integration.py — Integration tests for the full spin flow.

Tests the complete pipeline: SpinView → WeightEngine → PayoutCalculator →
LevelService → BonusService → JackpotPool.
"""

from decimal import Decimal
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import UserProfile
from apps.game.models import LevelConfig, JackpotPool


@override_settings(
    CHANNEL_LAYERS={
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
)
class SpinIntegrationTestCase(TestCase):
    """End-to-end tests for the spin API endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="spinner", password="testpass123"
        )
        self.profile = UserProfile.objects.create(
            user=self.user, balance=Decimal("1000.00"), level=1, xp=0
        )

        # Seed levels
        LevelConfig.objects.create(
            level=1, xp_required=0, bonus_coins=0,
            free_spins=0, prize_name="Newbie", prize_icon="🖱️"
        )
        LevelConfig.objects.create(
            level=2, xp_required=100, bonus_coins=50,
            free_spins=3, prize_name="Pendrive", prize_icon="🔌"
        )

        # Create jackpot pool
        JackpotPool.objects.create(
            id=1, current_amount=Decimal("1000.00")
        )

        # Auth
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

    def test_spin_success(self):
        """A spin with sufficient balance should succeed and return enriched data."""
        response = self.client.post(
            "/api/game/spin/",
            {"bet_amount": "10.00"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Verify response structure
        self.assertIn("reels", data)
        self.assertIn("payout", data)
        self.assertIn("combination_type", data)
        self.assertIn("xp_earned", data)
        self.assertIn("new_balance", data)
        self.assertIn("new_level", data)
        self.assertIn("new_xp", data)
        self.assertIn("free_spins_remaining", data)
        self.assertIn("bonuses", data)

        # Reels should be 5 symbol names
        self.assertEqual(len(data["reels"]), 5)
        self.assertIsInstance(data["reels"][0], str)

        # XP should have been earned
        self.assertGreater(data["xp_earned"], 0)

    def test_spin_insufficient_balance(self):
        """A spin with insufficient balance should be rejected."""
        self.profile.balance = Decimal("0.00")
        self.profile.save()

        response = self.client.post(
            "/api/game/spin/",
            {"bet_amount": "10.00"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_spin_deducts_balance(self):
        """A spin should deduct the bet from the player's balance."""
        initial_balance = float(self.profile.balance)

        response = self.client.post(
            "/api/game/spin/",
            {"bet_amount": "10.00"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # New balance should be <= initial - bet + payout
        expected_max = initial_balance - 10.00 + data["payout"]
        self.assertAlmostEqual(data["new_balance"], expected_max, places=2)

    def test_spin_with_free_spin(self):
        """A spin using a free spin should not deduct balance."""
        self.profile.free_spins = 5
        self.profile.save()
        initial_balance = float(self.profile.balance)

        response = self.client.post(
            "/api/game/spin/",
            {"bet_amount": "10.00", "use_free_spin": True},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Balance should not have been reduced by the bet
        # (it may have increased from payout)
        self.assertGreaterEqual(data["new_balance"], initial_balance - 0.01)
        self.assertEqual(data["free_spins_remaining"], 4)

    def test_spin_free_spin_unavailable(self):
        """Using free_spin when none available should be rejected."""
        self.profile.free_spins = 0
        self.profile.save()

        response = self.client.post(
            "/api/game/spin/",
            {"bet_amount": "10.00", "use_free_spin": True},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_jackpot_contribution(self):
        """Each spin should contribute 2% to the jackpot pool."""
        initial_jackpot = float(
            JackpotPool.objects.get(id=1).current_amount
        )

        self.client.post(
            "/api/game/spin/",
            {"bet_amount": "100.00"},
            format="json",
        )

        pool = JackpotPool.objects.get(id=1)
        expected_min = initial_jackpot + 2.00  # 2% of 100
        self.assertGreaterEqual(float(pool.current_amount), expected_min)

    def test_xp_accumulates_across_spins(self):
        """Multiple spins should accumulate XP."""
        for _ in range(5):
            self.client.post(
                "/api/game/spin/",
                {"bet_amount": "10.00"},
                format="json",
            )

        self.profile.refresh_from_db()
        self.assertGreater(self.profile.xp, 0)

    def test_invalid_bet_amount(self):
        """A negative or zero bet should be rejected."""
        response = self.client.post(
            "/api/game/spin/",
            {"bet_amount": "-5.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "/api/game/spin/",
            {"bet_amount": "0.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_spin_rejected(self):
        """An unauthenticated spin should be rejected."""
        client = APIClient()  # No credentials
        response = client.post(
            "/api/game/spin/",
            {"bet_amount": "10.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
