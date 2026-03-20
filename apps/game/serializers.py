from rest_framework import serializers
from .models import SpinHistory, LevelConfig, JackpotPool


class SpinHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpinHistory
        fields = '__all__'


class LevelConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelConfig
        fields = '__all__'


class JackpotPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = JackpotPool
        fields = '__all__'


class SpinRequestSerializer(serializers.Serializer):
    bet_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    use_free_spin = serializers.BooleanField(default=False, required=False)


class SpinResponseSerializer(serializers.Serializer):
    """Enriched response from a spin — used for API documentation."""
    spin_id = serializers.IntegerField()
    reels = serializers.ListField(child=serializers.CharField())
    payout = serializers.FloatField()
    combination_type = serializers.CharField()
    is_jackpot = serializers.BooleanField()
    multiplier = serializers.FloatField()
    free_spins_awarded = serializers.IntegerField()
    xp_earned = serializers.IntegerField()
    new_balance = serializers.FloatField()
    new_level = serializers.IntegerField()
    new_xp = serializers.IntegerField()
    free_spins_remaining = serializers.IntegerField()
    bonuses = serializers.ListField(child=serializers.DictField())
    winning_symbol = serializers.CharField(allow_null=True)
    wild_used = serializers.BooleanField()
