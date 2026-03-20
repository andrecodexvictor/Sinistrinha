"""
Shared pytest fixtures for Sinistrinha integration tests.
"""

import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.users.models import UserProfile
from apps.game.models import JackpotPool, LevelConfig
from apps.game.level_system import LEVEL_CONFIG


@pytest.fixture
def api_client():
    """Unauthenticated API client."""
    return APIClient()


@pytest.fixture
def user_with_balance(db):
    """Create a user with R$1000 balance."""
    user = User.objects.create_user(
        username='testplayer',
        email='test@sinistrinha.com',
        password='testpass123',
    )
    profile = UserProfile.objects.create(
        user=user,
        balance=Decimal('1000.00'),
        level=1,
        xp=0,
    )
    return user, profile


@pytest.fixture
def authenticated_client(user_with_balance):
    """Authenticated API client with a funded user."""
    user, profile = user_with_balance
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user, profile


@pytest.fixture
def jackpot_pool(db):
    """Initialize jackpot pool."""
    pool, _ = JackpotPool.objects.get_or_create(
        pk=1,
        defaults={'current_amount': Decimal('500.00'), 'min_amount': Decimal('500.00')},
    )
    return pool


@pytest.fixture
def level_configs(db):
    """Seed all level configurations."""
    configs = []
    for cfg in LEVEL_CONFIG:
        obj, _ = LevelConfig.objects.get_or_create(
            level=cfg['level'],
            defaults={
                'xp_required': cfg['xp'],
                'bonus_coins': cfg['bonus'],
                'free_spins': cfg['free_spins'],
                'prize_name': cfg['prize'],
                'prize_icon': cfg['icon'],
                'prize_rarity': cfg['rarity'],
            },
        )
        configs.append(obj)
    return configs


@pytest.fixture
def mock_probability_response():
    """Standard mock response from the probability engine."""
    return {
        'reels': ['ram', 'gpu_rtx', 'mouse', 'cpu', 'ram'],
        'payout_multiplier': 0.0,
        'payout': 0.0,
        'combination_type': 'loss',
        'matching_symbol': None,
        'match_count': 0,
        'wild_used': False,
        'near_miss_forced': False,
        'scatter_count': 0,
        'free_spins': 0,
        'xp_earned': 10,
        'session_rtp': 0.87,
        'reel_icons': ['💾', '🎮', '🖱️', '🔲', '💾'],
        'multiplier': 0.0,
        'is_jackpot': False,
        'xp_bonus': 10,
        'winning_symbol': None,
        'modifier_used': 1.0,
        'reasoning': {},
        'active_triggers': [],
    }


@pytest.fixture
def mock_win_response():
    """Mock response for a winning spin."""
    return {
        'reels': ['ram', 'ram', 'ram', 'cpu', 'mouse'],
        'payout_multiplier': 2.0,
        'payout': 10.0,
        'combination_type': '3x ram',
        'matching_symbol': 'ram',
        'match_count': 3,
        'wild_used': False,
        'near_miss_forced': False,
        'scatter_count': 0,
        'free_spins': 0,
        'xp_earned': 15,
        'session_rtp': 0.87,
        'reel_icons': ['💾', '💾', '💾', '🔲', '🖱️'],
        'multiplier': 2.0,
        'is_jackpot': False,
        'xp_bonus': 25,
        'winning_symbol': 'ram',
        'modifier_used': 1.0,
        'reasoning': {},
        'active_triggers': [],
    }
