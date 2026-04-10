import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone

from apps.users.models import UserProfile


class SpinHistory(models.Model):
    """Record of every spin played."""
    spin_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='spins')
    bet_amount = models.DecimalField(max_digits=12, decimal_places=2)
    result_reels = models.JSONField()  # ["ram", "gpu_rtx", "gorila_dourado", "cpu", "ram"]
    payout = models.DecimalField(max_digits=12, decimal_places=2)
    combination_type = models.CharField(max_length=100)  # 'JACKPOT 5x gorila_dourado', '3x mouse', 'loss'
    xp_earned = models.IntegerField(default=0)
    rtp_at_spin = models.FloatField(default=0.0)
    near_miss = models.BooleanField(default=False)
    is_free_spin = models.BooleanField(default=False)
    jackpot_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    wild_used = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"Spin {self.spin_id} by {self.user.user.username}"


class LevelConfig(models.Model):
    """Defines rewards and XP thresholds for each level."""
    level = models.IntegerField(unique=True)
    xp_required = models.IntegerField()
    bonus_coins = models.DecimalField(max_digits=12, decimal_places=2)
    free_spins = models.IntegerField(default=0)
    prize_name = models.CharField(max_length=100)
    prize_icon = models.CharField(max_length=100)
    prize_rarity = models.CharField(max_length=20, default="comum")
    house_edge_modifier = models.FloatField(default=1.0)

    class Meta:
        ordering = ['level']

    def __str__(self):
        return f"Level {self.level} — {self.prize_name}"


class JackpotPool(models.Model):
    """Progressive jackpot pool, shared across all players."""
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=500)
    contribution_rate = models.FloatField(default=0.02)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=500)
    last_won_by = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, blank=True
    )
    last_won_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Jackpot: R$ {self.current_amount}"


def _default_expiry():
    return timezone.now() + timedelta(hours=24)


class FreeSpin(models.Model):
    """Individual free spin token."""
    SOURCE_CHOICES = [
        ('level_up', 'Level Up'),
        ('scatter', 'Scatter Bonus'),
        ('promo', 'Promotion'),
        ('admin', 'Admin Grant'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='free_spins')
    bet_amount = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    is_used = models.BooleanField(default=False)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='level_up')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=_default_expiry)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['granted_at']
        indexes = [
            models.Index(fields=['user', 'is_used', 'expires_at']),
        ]

    def __str__(self):
        status = "used" if self.is_used else "available"
        return f"FreeSpin for {self.user.user.username} ({status})"
