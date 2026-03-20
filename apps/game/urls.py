from django.urls import path
from .views import (
    SpinView,
    JackpotView,
    RecentWinsView,
    LevelConfigView,
    UserSpinHistoryView,
    FreeSpinView,
    LevelProgressView,
)

urlpatterns = [
    path('spin/', SpinView.as_view(), name='game_spin'),
    path('jackpot/', JackpotView.as_view(), name='game_jackpot'),
    path('recent-wins/', RecentWinsView.as_view(), name='game_recent_wins'),
    path('level-config/', LevelConfigView.as_view(), name='game_level_config'),
    path('level-progress/', LevelProgressView.as_view(), name='game_level_progress'),
    path('free-spins/', FreeSpinView.as_view(), name='game_free_spins'),
    path('user/history/', UserSpinHistoryView.as_view(), name='user_spin_history'),
]
