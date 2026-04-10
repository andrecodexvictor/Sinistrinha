"""
test_level_service.py — Unit tests for the LevelService.
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User

from apps.users.models import UserProfile
from apps.game.models import LevelConfig
from apps.game.services.level_service import LevelService


class LevelServiceTestCase(TestCase):
    """Tests for XP awarding, level-up, and RTP lookup."""

    def setUp(self):
        """Create a test user and seed level configs."""
        self.user = User.objects.create_user(
            username="testplayer", password="testpass123"
        )
        self.profile = UserProfile.objects.create(
            user=self.user, balance=Decimal("1000.00"), level=1, xp=0
        )

        # Seed levels 1-5 for testing
        LevelConfig.objects.create(
            level=1, xp_required=0, bonus_coins=0,
            free_spins=0, prize_name="Newbie", prize_icon="🖱️"
        )
        LevelConfig.objects.create(
            level=2, xp_required=500, bonus_coins=50,
            free_spins=3, prize_name="Pendrive 8GB", prize_icon="🔌"
        )
        LevelConfig.objects.create(
            level=3, xp_required=1500, bonus_coins=150,
            free_spins=5, prize_name="Teclado", prize_icon="⌨️"
        )
        LevelConfig.objects.create(
            level=4, xp_required=3500, bonus_coins=350,
            free_spins=7, prize_name="Mouse Gamer", prize_icon="🖱️",
            house_edge_modifier=1.02
        )
        LevelConfig.objects.create(
            level=5, xp_required=7000, bonus_coins=700,
            free_spins=10, prize_name="RAM DDR5", prize_icon="💾",
            house_edge_modifier=1.02
        )

    def test_award_xp_no_level_up(self):
        """XP below next level threshold should not trigger level-up."""
        event = LevelService.award_xp(self.profile, 100)
        self.profile.refresh_from_db()

        self.assertIsNone(event)
        self.assertEqual(self.profile.xp, 100)
        self.assertEqual(self.profile.level, 1)

    def test_award_xp_triggers_level_up(self):
        """XP reaching next level threshold should trigger level-up."""
        event = LevelService.award_xp(self.profile, 600)
        self.profile.refresh_from_db()

        self.assertIsNotNone(event)
        self.assertEqual(event.old_level, 1)
        self.assertEqual(event.new_level, 2)
        self.assertEqual(event.bonus_coins, 50.0)
        self.assertEqual(event.free_spins, 3)
        self.assertEqual(self.profile.level, 2)
        self.assertEqual(self.profile.xp, 600)

    def test_multi_level_jump(self):
        """Large XP award should handle jumping multiple levels."""
        event = LevelService.award_xp(self.profile, 2000)
        self.profile.refresh_from_db()

        self.assertIsNotNone(event)
        self.assertEqual(event.old_level, 1)
        self.assertEqual(event.new_level, 3)
        # Should accumulate bonuses from level 2 + level 3
        self.assertEqual(event.bonus_coins, 200.0)  # 50 + 150
        self.assertEqual(event.free_spins, 8)  # 3 + 5

    def test_xp_accumulation(self):
        """XP should accumulate across multiple awards."""
        LevelService.award_xp(self.profile, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.xp, 200)

        LevelService.award_xp(self.profile, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.xp, 400)

    def test_max_level_no_further_level_up(self):
        """At max level, no further level-ups should occur."""
        self.profile.level = 5
        self.profile.xp = 10000
        self.profile.save()

        event = LevelService.award_xp(self.profile, 50000)
        self.profile.refresh_from_db()

        self.assertIsNone(event)
        self.assertEqual(self.profile.level, 5)

    def test_get_current_rtp_known_level(self):
        """RTP should be returned for known levels."""
        self.profile.level = 5
        rtp = LevelService.get_current_rtp(self.profile)
        self.assertEqual(rtp, 0.87)

    def test_get_current_rtp_above_max(self):
        """RTP for levels above max should use highest defined RTP."""
        self.profile.level = 99
        rtp = LevelService.get_current_rtp(self.profile)
        self.assertEqual(rtp, 0.895)  # Level 10 RTP

    def test_get_rtp_modifier(self):
        """Modifier should increase with higher levels."""
        self.profile.level = 1
        mod_1 = LevelService.get_rtp_modifier(self.profile)

        self.profile.level = 5
        mod_5 = LevelService.get_rtp_modifier(self.profile)

        self.assertGreater(mod_5, mod_1)

    def test_level_up_event_to_dict(self):
        """LevelUpEvent.to_dict should return a proper dictionary."""
        event = LevelService.award_xp(self.profile, 600)
        self.assertIsNotNone(event)

        d = event.to_dict()
        self.assertIn("old_level", d)
        self.assertIn("new_level", d)
        self.assertIn("bonus_coins", d)
        self.assertIn("free_spins", d)
        self.assertIn("prize_name", d)
