"""
test_full_spin_flow.py — End-to-end spin integration tests.

Tests the complete flow from registration through multiple spins,
verifying balance changes, XP accumulation, and history recording.
"""

import pytest
from decimal import Decimal
from unittest.mock import patch

from django.test import override_settings
from rest_framework import status


@pytest.mark.django_db
class TestCompleteSpinFlow:
    """Tests the full spin lifecycle."""

    @patch('apps.game.views._payout_calculator.calculate')
    @patch('apps.game.views._weight_engine.spin_all')
    def test_single_spin_loss(
        self, mock_spin_all, mock_calculate, authenticated_client, jackpot_pool,
        mock_probability_response
    ):
        """Test a single losing spin debits balance and records history."""
        client, user, profile = authenticated_client
        mock_spin_all.return_value = mock_probability_response['reels']
        mock_calculate.return_value = mock_probability_response

        initial_balance = profile.balance
        resp = client.post('/api/game/spin/', {'bet_amount': '5.00'})

        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()

        assert data['combination_type'] == 'loss'
        assert Decimal(str(data['payout'])) == Decimal('0')
        assert Decimal(str(data['new_balance'])) < initial_balance
        assert data['xp_earned'] > 0
        assert data['spin_id'] is not None

    @patch('apps.game.views._payout_calculator.calculate')
    @patch('apps.game.views._weight_engine.spin_all')
    def test_single_spin_win(
        self, mock_spin_all, mock_calculate, authenticated_client, jackpot_pool,
        mock_win_response
    ):
        """Test a winning spin credits balance correctly."""
        client, user, profile = authenticated_client
        mock_spin_all.return_value = mock_win_response['reels']
        mock_calculate.return_value = mock_win_response

        resp = client.post('/api/game/spin/', {'bet_amount': '5.00'})
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()

        assert Decimal(str(data['payout'])) > 0
        assert data['combination_type'] == '3x ram'

    def test_spin_insufficient_balance(
        self, authenticated_client, jackpot_pool
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

    def test_bet_below_minimum(
        self, authenticated_client, jackpot_pool
    ):
        """Test bet below R$0.10 is rejected."""
        client, user, profile = authenticated_client
        resp = client.post('/api/game/spin/', {'bet_amount': '0.05'})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_bet_above_maximum(
        self, authenticated_client, jackpot_pool
    ):
        """Test bet above max is rejected (10% of balance or R$500)."""
        client, user, profile = authenticated_client
        # Balance is R$1000, so max is min(500, 100) = R$100
        resp = client.post('/api/game/spin/', {'bet_amount': '150.00'})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @patch('apps.game.views._payout_calculator.calculate')
    @patch('apps.game.views._weight_engine.spin_all')
    def test_multiple_spins_accumulate_xp(
        self, mock_spin_all, mock_calculate, authenticated_client, jackpot_pool,
        mock_probability_response
    ):
        """Test that XP accumulates across multiple spins."""
        client, user, profile = authenticated_client
        mock_spin_all.return_value = mock_probability_response['reels']
        mock_calculate.return_value = mock_probability_response

        total_xp = 0
        for _ in range(5):
            resp = client.post('/api/game/spin/', {'bet_amount': '1.00'})
            assert resp.status_code == status.HTTP_200_OK
            data = resp.json()
            total_xp = data['new_xp']

        assert total_xp > 0

    @patch('apps.game.views._payout_calculator.calculate')
    @patch('apps.game.views._weight_engine.spin_all')
    def test_jackpot_pool_grows_with_bets(
        self, mock_spin_all, mock_calculate, authenticated_client, jackpot_pool,
        mock_probability_response
    ):
        """Test that jackpot pool increases with each bet."""
        client, user, profile = authenticated_client
        mock_spin_all.return_value = mock_probability_response['reels']
        mock_calculate.return_value = mock_probability_response

        initial_jackpot = Decimal(str(jackpot_pool.current_amount))

        for _ in range(5):
            resp = client.post('/api/game/spin/', {'bet_amount': '10.00'})
            assert resp.status_code == status.HTTP_200_OK

        jackpot_pool.refresh_from_db()
        assert jackpot_pool.current_amount > initial_jackpot

    @patch('apps.game.views._payout_calculator.calculate')
    @patch('apps.game.views._weight_engine.spin_all')
    def test_spin_history_recorded(
        self, mock_spin_all, mock_calculate, authenticated_client, jackpot_pool,
        mock_probability_response
    ):
        """Test that each spin creates a SpinHistory record."""
        client, user, profile = authenticated_client
        mock_spin_all.return_value = mock_probability_response['reels']
        mock_calculate.return_value = mock_probability_response

        client.post('/api/game/spin/', {'bet_amount': '5.00'})

        resp = client.get('/api/game/user/history/')
        assert resp.status_code == status.HTTP_200_OK
        results = resp.json().get('results', resp.json())
        assert len(results) >= 1
