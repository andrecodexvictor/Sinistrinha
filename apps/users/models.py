from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    level = models.IntegerField(default=1)
    xp = models.IntegerField(default=0)
    total_spins = models.IntegerField(default=0)
    total_wagered = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_won = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    free_spins = models.IntegerField(default=0)
    current_multiplier = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    avatar_url = models.URLField(blank=True)
    is_vip = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"
