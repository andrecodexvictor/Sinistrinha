"""
test_full_spin_flow.py — End-to-end spin integration tests.

Tests the complete flow from registration through multiple spins,
verifying balance changes, XP accumulation, and history recording.
"""

import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import override_settings
from rest_framework import status


@pytest.mark.django_db
class TestCompleteSpinFlow:
    """Tests the full spin lifecycle."""

    @patch('apps.game.views.requests.post')
    def test_single_spin_loss(
        self, mock_post, authenticated_client, jackpot_pool,
        mock_probability_response
    ):
        """Test a single losing spin debits balance and records history."""
        client, user, profile = authenticated_client
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_probability_response,
            raise_for_status=lambda: None,
        )

        initial_balance = profile.balance
        resp = client.post('/api/game/spin/', {'bet_amount': '5.00'})

        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()

        assert data['combination_type'] == 'loss'
        assert Decimal(data['payout']) == Decimal('0')
        assert Decimal(data['new_balance']) < initial_balance
        assert data['xp_earned'] > 0
        assert data['spin_id'] is not None

    @patch('apps.game.views.requests.post')
    def test_single_spin_win(
        self, mock_post, authenticated_client, jackpot_pool,
        mock_win_response
    ):
        """Test a winning spin credits balance correctly."""
        client, user, profile = authenticated_client
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_win_response,
            raise_for_status=lambda: None,
        )

        resp = client.post('/api/game/spin/', {'bet_amount': '5.00'})
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()

        assert Decimal(data['payout']) > 0
        assert data['combination_type'] == '3x ram'

    @patch('apps.game.views.requests.post')
    def test_spin_insufficient_balance(
        self, mock_post, authenticated_client, jackpot_pool
    ):
        """Test spin rejected when balance is too low."""
        client, user, profile = authenticated_client
        profile.balance = Decimal('0.05')
        profile.save()

        resp = client.post('/api/game/spin/', {'bet_amount': '5.00'})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_spin_unauthenticated(self, api_client):
        """Test spin requires authentication."""
        resp = api_client.post('/api/game/spin/', {'bet_amount': '5.00'})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('apps.game.views.requests.post')
    def test_bet_below_minimum(
        self, mock_post, authenticated_client, jackpot_pool
    ):
        """Test bet below R$0.10 is rejected."""
        client, user, profile = authenticated_client
        resp = client.post('/api/game/spin/', {'bet_amount': '0.05'})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @patch('apps.game.views.requests.post')
    def test_bet_above_maximum(
        self, mock_post, authenticated_client, jackpot_pool
    ):
        """Test bet above max is rejected (10% of balance or R$500)."""
        client, user, profile = authenticated_client
        # Balance is R$1000, so max is min(500, 100) = R$100
        resp = client.post('/api/game/spin/', {'bet_amount': '150.00'})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @patch('apps.game.views.requests.post')
    def test_multiple_spins_accumulate_xp(
        self, mock_post, authenticated_client, jackpot_pool,
        mock_probability_response
    ):
        """Test that XP accumulates across multiple spins."""
        client, user, profile = authenticated_client
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_probability_response,
            raise_for_status=lambda: None,
        )

        total_xp = 0
        for _ in range(5):
            resp = client.post('/api/game/spin/', {'bet_amount': '1.00'})
            assert resp.status_code == status.HTTP_200_OK
            data = resp.json()
            total_xp = data['new_xp']

        assert total_xp > 0

    @patch('apps.game.views.requests.post')
    def test_jackpot_pool_grows_with_bets(
        self, mock_post, authenticated_client, jackpot_pool,
        mock_probability_response
    ):
        """Test that jackpot pool increases with each bet."""
        client, user, profile = authenticated_client
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_probability_response,
            raise_for_status=lambda: None,
        )

        initial_jackpot = Decimal(str(jackpot_pool.current_amount))

        for _ in range(5):
            resp = client.post('/api/game/spin/', {'bet_amount': '10.00'})
            assert resp.status_code == status.HTTP_200_OK

        jackpot_pool.refresh_from_db()
        assert jackpot_pool.current_amount > initial_jackpot

    @patch('apps.game.views.requests.post')
    def test_spin_history_recorded(
        self, mock_post, authenticated_client, jackpot_pool,
        mock_probability_response
    ):
        """Test that each spin creates a SpinHistory record."""
        client, user, profile = authenticated_client
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_probability_response,
            raise_for_status=lambda: None,
        )

        client.post('/api/game/spin/', {'bet_amount': '5.00'})

        resp = client.get('/api/game/user/history/')
        assert resp.status_code == status.HTTP_200_OK
        results = resp.json().get('results', resp.json())
        assert len(results) >= 1

    @patch('apps.game.views.requests.post')
    def test_probability_engine_failure_refunds_bet(
        self, mock_post, authenticated_client, jackpot_pool
    ):
        """Test that bet is refunded if probability engine is down."""
        client, user, profile = authenticated_client
        initial_balance = profile.balance

        import requests as req
        mock_post.side_effect = req.ConnectionError("Engine down")

        resp = client.post('/api/game/spin/', {'bet_amount': '5.00'})
        assert resp.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

        profile.refresh_from_db()
        assert profile.balance == initial_balance
