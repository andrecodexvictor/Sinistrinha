"""
admin.py — Custom Django admin for Sinistrinha casino dashboard.

Registers all game models and provides a custom dashboard view
with RTP monitoring, big wins feed, and user analytics.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib import admin
from django.db.models import Avg, Count, Sum, Q
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone

from .models import FreeSpin, JackpotPool, LevelConfig, SpinHistory


# --------------------------------------------------------------------------- #
# Model Admins
# --------------------------------------------------------------------------- #

@admin.register(SpinHistory)
class SpinHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'spin_id', 'get_username', 'bet_amount', 'payout',
        'combination_type', 'xp_earned', 'near_miss', 'is_free_spin', 'timestamp',
    ]
    list_filter = ['combination_type', 'near_miss', 'is_free_spin', 'timestamp']
    search_fields = ['user__user__username', 'spin_id']
    readonly_fields = [
        'spin_id', 'user', 'bet_amount', 'result_reels', 'payout',
        'combination_type', 'xp_earned', 'rtp_at_spin', 'near_miss',
        'is_free_spin', 'jackpot_contribution', 'wild_used', 'timestamp',
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    @admin.display(description='User')
    def get_username(self, obj):
        return obj.user.user.username


@admin.register(LevelConfig)
class LevelConfigAdmin(admin.ModelAdmin):
    list_display = ['level', 'xp_required', 'bonus_coins', 'free_spins', 'prize_name', 'prize_rarity']
    ordering = ['level']


@admin.register(JackpotPool)
class JackpotPoolAdmin(admin.ModelAdmin):
    list_display = ['current_amount', 'contribution_rate', 'min_amount', 'last_won_at']
    readonly_fields = ['last_won_by', 'last_won_at']


@admin.register(FreeSpin)
class FreeSpinAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'bet_amount', 'is_used', 'source', 'granted_at', 'expires_at']
    list_filter = ['is_used', 'source']
    search_fields = ['user__user__username']

    @admin.display(description='User')
    def get_username(self, obj):
        return obj.user.user.username


# --------------------------------------------------------------------------- #
# Custom Dashboard View
# --------------------------------------------------------------------------- #

class CasinoDashboardAdminSite(admin.AdminSite):
    """Extended admin site with casino dashboard."""

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('casino/dashboard/', self.admin_view(self.dashboard_view), name='casino_dashboard'),
            path('casino/big-wins/', self.admin_view(self.big_wins_view), name='casino_big_wins'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        """Casino observability dashboard."""
        now = timezone.now()

        # Time windows
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)

        # RTP calculations
        def calc_rtp(since):
            stats = SpinHistory.objects.filter(timestamp__gte=since).aggregate(
                total_wagered=Sum('bet_amount'),
                total_paid=Sum('payout'),
                spin_count=Count('id'),
                near_miss_count=Count('id', filter=Q(near_miss=True)),
            )
            wagered = stats['total_wagered'] or Decimal('0')
            paid = stats['total_paid'] or Decimal('0')
            rtp = (float(paid) / float(wagered) * 100) if wagered > 0 else 0
            return {
                'rtp': round(rtp, 2),
                'wagered': wagered,
                'paid': paid,
                'spins': stats['spin_count'] or 0,
                'near_misses': stats['near_miss_count'] or 0,
                'house_edge': round(100 - rtp, 2),
            }

        rtp_24h = calc_rtp(last_24h)
        rtp_7d = calc_rtp(last_7d)
        rtp_30d = calc_rtp(last_30d)

        # Jackpot
        try:
            jackpot = JackpotPool.objects.get(pk=1)
        except JackpotPool.DoesNotExist:
            jackpot = None

        # Recent big wins (>R$100)
        big_wins = (
            SpinHistory.objects
            .filter(payout__gte=100)
            .select_related('user__user')
            .order_by('-timestamp')[:20]
        )

        # Active users (spun in last hour)
        active_users_count = (
            SpinHistory.objects
            .filter(timestamp__gte=now - timedelta(hours=1))
            .values('user')
            .distinct()
            .count()
        )

        # Spins per hour (last 24h)
        spins_per_hour = []
        for h in range(24):
            start = now - timedelta(hours=h + 1)
            end = now - timedelta(hours=h)
            count = SpinHistory.objects.filter(
                timestamp__gte=start, timestamp__lt=end
            ).count()
            spins_per_hour.append({
                'hour': f'{h}h ago',
                'count': count,
            })

        context = {
            **self.each_context(request),
            'title': 'Casino Dashboard — Sinistrinha',
            'rtp_24h': rtp_24h,
            'rtp_7d': rtp_7d,
            'rtp_30d': rtp_30d,
            'target_rtp': 87.0,
            'jackpot': jackpot,
            'big_wins': big_wins,
            'active_users_count': active_users_count,
            'spins_per_hour': spins_per_hour,
        }

        return TemplateResponse(request, 'admin/casino_dashboard.html', context)

    def big_wins_view(self, request):
        """Detailed big wins list with filtering."""
        min_payout = request.GET.get('min_payout', 100)

        wins = (
            SpinHistory.objects
            .filter(payout__gte=min_payout)
            .select_related('user__user')
            .order_by('-timestamp')
        )

        context = {
            **self.each_context(request),
            'title': 'Big Wins — Sinistrinha',
            'wins': wins[:200],
            'min_payout': min_payout,
            'total_count': wins.count(),
        }

        return TemplateResponse(request, 'admin/casino_big_wins.html', context)
