"""
views.py — Game API views.

The SpinView integrates the full game pipeline:
WeightEngine → PayoutCalculator → LevelService → BonusService → NotificationService.
"""

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from decimal import Decimal

from .models import SpinHistory, LevelConfig, JackpotPool
from apps.users.models import UserProfile
from .serializers import (
    SpinHistorySerializer,
    LevelConfigSerializer,
    JackpotPoolSerializer,
    SpinRequestSerializer,
    SpinResponseSerializer,
)
from .services.level_service import LevelService
from .services.bonus_service import BonusService
from .services.notification_service import NotificationService

from probability_engine.weight_engine import WeightEngine
from probability_engine.payout_calculator import PayoutCalculator

import logging

logger = logging.getLogger(__name__)

# Singleton instances for the probability engine
_weight_engine = WeightEngine()
_payout_calculator = PayoutCalculator()


class SpinView(views.APIView):
    """
    Execute a slot machine spin.

    Integrates: WeightEngine → PayoutCalculator → JackpotPool →
    LevelService → BonusService → NotificationService.
    """
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        serializer = SpinRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        bet_amount = serializer.validated_data['bet_amount']
        use_free_spin = serializer.validated_data.get('use_free_spin', False)
        user_profile = request.user.profile

        # 1. Check balance or free spin availability
        if use_free_spin:
            if not BonusService.consume_free_spin(user_profile):
                return Response(
                    {"error": "No free spins available"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Free spins use a fixed minimum bet
            bet_amount = min(bet_amount, Decimal("10.00"))
        else:
            if user_profile.balance < bet_amount:
                return Response(
                    {"error": "Insufficient balance"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Deduct balance
            user_profile.balance -= bet_amount

        user_profile.total_wagered += bet_amount
        user_profile.total_spins += 1

        # 2. Get RTP modifier based on player level
        modifier = LevelService.get_rtp_modifier(user_profile)

        # 3. Spin reels using weighted probability engine
        reels = _weight_engine.spin_all(modifier=modifier)

        # 4. Calculate payout
        result = _payout_calculator.calculate(reels, float(bet_amount))

        payout = Decimal(str(result["payout"]))
        combination_type = result["combination_type"]
        is_jackpot = result["is_jackpot"]
        free_spins_awarded = result["free_spins"]
        xp_earned = result["xp_bonus"]

        # 5. Apply payout
        if payout > 0:
            user_profile.balance += payout
            user_profile.total_won += payout

        # 6. Jackpot pool contribution (2% of every bet)
        self._contribute_to_jackpot(bet_amount)

        # 7. Award XP and check for level-up
        old_level = user_profile.level
        level_up_event = LevelService.award_xp(user_profile, xp_earned)

        # 8. Grant free spins from scatter results
        bonuses = []
        if free_spins_awarded > 0:
            BonusService.grant_free_spins(
                user_profile, free_spins_awarded, reason="scatter_bonus"
            )
            bonuses.append({
                "type": "free_spins",
                "count": free_spins_awarded,
                "reason": "scatter_bonus",
            })

        if level_up_event:
            bonuses.append({
                "type": "level_up",
                "old_level": level_up_event.old_level,
                "new_level": level_up_event.new_level,
                "bonus_coins": level_up_event.bonus_coins,
                "free_spins": level_up_event.free_spins,
                "prize_name": level_up_event.prize_name,
            })

        # 9. Save profile (xp and level already saved by LevelService)
        user_profile.save()

        # 10. Save spin history
        rtp_at_spin = LevelService.get_current_rtp(user_profile) * 100
        spin = SpinHistory.objects.create(
            user=user_profile,
            bet_amount=bet_amount,
            result_reels=reels,
            payout=payout,
            combination_type=combination_type,
            xp_earned=xp_earned,
            rtp_at_spin=rtp_at_spin,
        )

        # 11. Broadcast events via WebSocket
        self._broadcast_events(
            request.user, user_profile, payout,
            combination_type, is_jackpot, reels,
            level_up_event,
        )

        # 12. Build enriched response
        response_data = {
            "spin_id": spin.id,
            "reels": reels,
            "payout": float(payout),
            "combination_type": combination_type,
            "is_jackpot": is_jackpot,
            "multiplier": result["multiplier"],
            "free_spins_awarded": free_spins_awarded,
            "xp_earned": xp_earned,
            "new_balance": float(user_profile.balance),
            "new_level": user_profile.level,
            "new_xp": user_profile.xp,
            "free_spins_remaining": user_profile.free_spins,
            "bonuses": bonuses,
            "winning_symbol": result["winning_symbol"],
            "wild_used": result["wild_used"],
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @staticmethod
    def _contribute_to_jackpot(bet_amount: Decimal) -> None:
        """Add 2% of the bet to the progressive jackpot pool (race-safe)."""
        try:
            from .jackpot import JackpotSystem
            JackpotSystem().contribute(bet_amount)
        except Exception as e:
            logger.error(f"Failed to update jackpot pool: {e}")

    @staticmethod
    def _broadcast_events(
        user, profile, payout, combination_type, is_jackpot, reels, level_up_event
    ) -> None:
        """Send real-time events to WebSocket channels."""
        try:
            # Private: balance update
            NotificationService.notify_balance_update(
                user.id, float(profile.balance)
            )

            # Private: free spins update
            NotificationService.notify_free_spins_update(
                user.id, profile.free_spins
            )

            # Public: broadcast significant wins (payout > 5x bet or jackpot)
            if payout > 0 and (is_jackpot or float(payout) >= 50):
                winning_symbol = None
                if reels:
                    from probability_engine.config import SYMBOLS
                    sym = SYMBOLS.get(reels[0])
                    winning_symbol = sym.icon if sym else reels[0]

                NotificationService.broadcast_recent_win(
                    username=user.username,
                    amount=float(payout),
                    symbol=winning_symbol or "🎰",
                    is_jackpot=is_jackpot,
                )

            # Private: level-up notification
            if level_up_event:
                NotificationService.notify_level_up(
                    user_id=user.id,
                    old_level=level_up_event.old_level,
                    new_level=level_up_event.new_level,
                    bonus_coins=level_up_event.bonus_coins,
                    free_spins=level_up_event.free_spins,
                    prize_name=level_up_event.prize_name,
                )

            # Public: jackpot update
            try:
                pool = JackpotPool.objects.get(id=1)
                NotificationService.broadcast_jackpot_update(
                    float(pool.current_amount)
                )
            except JackpotPool.DoesNotExist:
                pass

        except Exception as e:
            logger.error(f"Failed to broadcast events: {e}")


class JackpotView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = JackpotPoolSerializer

    def get_object(self):
        pool, _ = JackpotPool.objects.get_or_create(
            id=1, defaults={"current_amount": 1000.0}
        )
        return pool


class RecentWinsView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SpinHistorySerializer

    def get_queryset(self):
        return SpinHistory.objects.filter(payout__gt=0).order_by('-timestamp')[:20]


class LevelConfigView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LevelConfigSerializer
    queryset = LevelConfig.objects.all()


class UserSpinHistoryView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SpinHistorySerializer

    def get_queryset(self):
        return SpinHistory.objects.filter(
            user=self.request.user.profile
        ).order_by('-timestamp')


class FreeSpinView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        from .free_spins import FreeSpinSystem
        fs_system = FreeSpinSystem()
        info = fs_system.get_free_spin_info(request.user.profile)
        return Response(info, status=status.HTTP_200_OK)


class LevelProgressView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = request.user.profile
        try:
            current_level_config = LevelConfig.objects.get(level=profile.level)
            next_level_config = LevelConfig.objects.filter(level__gt=profile.level).order_by('level').first()
            xp_required_next = next_level_config.xp_required if next_level_config else current_level_config.xp_required
            
            data = {
                "level": profile.level,
                "current_xp": profile.xp,
                "next_level_xp": xp_required_next,
                "is_max_level": next_level_config is None,
            }
        except LevelConfig.DoesNotExist:
            data = {
                "level": profile.level,
                "current_xp": profile.xp,
                "next_level_xp": 100,
                "is_max_level": False,
            }
        return Response(data, status=status.HTTP_200_OK)
