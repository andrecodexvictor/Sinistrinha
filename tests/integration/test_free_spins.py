"""
test_free_spins.py — Free spin system integration tests.
"""

import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.utils import timezone
from datetime import timedelta

from apps.game.free_spins import FreeSpinSystem
from apps.game.models import FreeSpin


@pytest.mark.django_db
class TestFreeSpinSystem:
    """Test free spin grant/consume/expiry lifecycle."""

    def test_grant_free_spins(self, user_with_balance):
        """Test granting free spins creates records."""
        user, profile = user_with_balance
        system = FreeSpinSystem()

        count = system.grant_free_spins(profile, 5, Decimal('2.00'), 'level_up')
        assert count == 5
        assert FreeSpin.objects.filter(user=profile, is_used=False).count() == 5

    def test_use_free_spin(self, user_with_balance):
        """Test consuming a free spin."""
        user, profile = user_with_balance
        system = FreeSpinSystem()

        system.grant_free_spins(profile, 3, Decimal('5.00'), 'scatter')
        result = system.use_free_spin(profile)

        assert result is not None
        assert result['bet_amount'] == 5.0
        assert result['source'] == 'scatter'
        assert system.get_remaining(profile) == 2

    def test_use_free_spin_none_available(self, user_with_balance):
        """Test consuming when no free spins available returns None."""
        user, profile = user_with_balance
        system = FreeSpinSystem()

        result = system.use_free_spin(profile)
        assert result is None

    def test_expired_free_spins_not_usable(self, user_with_balance):
        """Test that expired free spins cannot be consumed."""
        user, profile = user_with_balance
        system = FreeSpinSystem()

        system.grant_free_spins(profile, 2, Decimal('1.00'))

        # Force-expire all free spins
        FreeSpin.objects.filter(user=profile).update(
            expires_at=timezone.now() - timedelta(hours=1)
        )

        result = system.use_free_spin(profile)
        assert result is None
        assert system.get_remaining(profile) == 0

    def test_get_free_spin_info(self, user_with_balance):
        """Test free spin info endpoint data."""
        user, profile = user_with_balance
        system = FreeSpinSystem()

        system.grant_free_spins(profile, 3, Decimal('10.00'))
        info = system.get_free_spin_info(profile)

        assert info['available'] == 3
        assert info['next_expiry'] is not None
        assert info['total_used'] == 0

    @patch('apps.game.views.requests.post')
    def test_free_spin_via_spin_endpoint(
        self, mock_post, authenticated_client, jackpot_pool,
        mock_win_response
    ):
        """Test using a free spin through the spin endpoint."""
        client, user, profile = authenticated_client
        system = FreeSpinSystem()

        # Grant free spins
        system.grant_free_spins(profile, 2, Decimal('5.00'))

        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_win_response,
            raise_for_status=lambda: None,
        )

        initial_balance = profile.balance
        resp = client.post('/api/game/spin/', {
            'bet_amount': '5.00',
            'use_free_spin': True,
        })

        assert resp.status_code == 200
        data = resp.json()
        assert data['is_free_spin'] is True

        # Balance should NOT decrease (free spin doesn't cost money)
        # but payout should be credited
        profile.refresh_from_db()
        assert profile.balance >= initial_balance

    @patch('apps.game.views.requests.post')
    def test_scatter_awards_free_spins(
        self, mock_post, authenticated_client, jackpot_pool
    ):
        """Test that scatter symbols in result grant free spins."""
        client, user, profile = authenticated_client

        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                'reels': ['scatter_banana', 'pendrive', 'scatter_banana', 'mouse', 'scatter_banana'],
                'payout': 7.5,
                'combination_type': 'scatter_win',
                'near_miss_forced': False,
                'wild_used': False,
                'free_spins': 5,
                'xp_earned': 15,
                'session_rtp': 0.87,
                'reel_icons': ['🍌', '🔌', '🍌', '🖱️', '🍌'],
                'multiplier': 1.5,
                'is_jackpot': False,
                'xp_bonus': 25,
                'winning_symbol': 'scatter_banana',
                'match_count': 3,
                'payout_multiplier': 1.5,
                'scatter_count': 3,
                'modifier_used': 1.0,
                'reasoning': {},
                'active_triggers': [],
            },
            raise_for_status=lambda: None,
        )

        resp = client.post('/api/game/spin/', {'bet_amount': '5.00'})
        assert resp.status_code == 200
        data = resp.json()

        assert data['free_spins_awarded'] == 5
        assert data['free_spins_remaining'] == 5
