"""
test_jackpot.py — Jackpot system integration tests.
"""

import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock

from apps.game.jackpot import JackpotSystem, JACKPOT_MINIMUM
from apps.game.models import JackpotPool


@pytest.mark.django_db
class TestJackpotSystem:
    """Test the progressive jackpot system."""

    def test_contribute_increases_pool(self, jackpot_pool):
        """2% of each bet goes to the jackpot pool."""
        system = JackpotSystem()
        initial = jackpot_pool.current_amount

        contribution = system.contribute(Decimal('100.00'))

        assert contribution == Decimal('2.00')
        jackpot_pool.refresh_from_db()
        assert jackpot_pool.current_amount == initial + Decimal('2.00')

    def test_check_jackpot_win_true(self):
        """5x gorila_dourado triggers jackpot."""
        assert JackpotSystem.check_jackpot_win(
            ['gorila_dourado'] * 5
        ) is True

    def test_check_jackpot_win_false(self):
        """Anything other than 5x gorila_dourado does not trigger."""
        assert JackpotSystem.check_jackpot_win(
            ['gorila_dourado', 'gorila_dourado', 'ram', 'gorila_dourado', 'gorila_dourado']
        ) is False

    def test_pay_jackpot_credits_winner(self, jackpot_pool, user_with_balance):
        """Jackpot payment credits winner and resets pool."""
        user, profile = user_with_balance
        system = JackpotSystem()

        # Inflate jackpot
        jackpot_pool.current_amount = Decimal('5000.00')
        jackpot_pool.save()

        initial_balance = profile.balance
        amount = system.pay_jackpot(profile)

        assert amount == Decimal('5000.00')
        profile.refresh_from_db()
        assert profile.balance == initial_balance + Decimal('5000.00')

        jackpot_pool.refresh_from_db()
        assert jackpot_pool.current_amount == JACKPOT_MINIMUM
        assert jackpot_pool.last_won_by == profile

    def test_get_current_amount(self, jackpot_pool):
        """get_current_amount returns the pool value."""
        system = JackpotSystem()
        amount = system.get_current_amount()
        assert amount == float(jackpot_pool.current_amount)

    @patch('apps.game.views.requests.post')
    def test_jackpot_win_via_spin(
        self, mock_post, authenticated_client, jackpot_pool
    ):
        """Test jackpot win through the spin endpoint."""
        client, user, profile = authenticated_client

        # Inflate jackpot
        jackpot_pool.current_amount = Decimal('10000.00')
        jackpot_pool.save()

        # Mock probability engine returning jackpot reels
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                'reels': ['gorila_dourado'] * 5,
                'payout': 750.0,  # base payout from engine
                'combination_type': 'JACKPOT 5x gorila_dourado',
                'near_miss_forced': False,
                'wild_used': False,
                'free_spins': 0,
                'xp_earned': 100,
                'session_rtp': 0.87,
                'reel_icons': ['🦍'] * 5,
                'multiplier': 150.0,
                'is_jackpot': True,
                'xp_bonus': 500,
                'winning_symbol': 'gorila_dourado',
                'match_count': 5,
                'payout_multiplier': 150.0,
                'scatter_count': 0,
                'modifier_used': 1.0,
                'reasoning': {},
                'active_triggers': [],
            },
            raise_for_status=lambda: None,
        )

        initial_balance = profile.balance
        resp = client.post('/api/game/spin/', {'bet_amount': '5.00'})
        assert resp.status_code == 200
        data = resp.json()

        # Jackpot should have been paid
        profile.refresh_from_db()
        assert profile.balance > initial_balance

        # Jackpot pool should reset
        jackpot_pool.refresh_from_db()
        assert jackpot_pool.current_amount == JACKPOT_MINIMUM
