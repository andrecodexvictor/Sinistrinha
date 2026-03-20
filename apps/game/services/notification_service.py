"""
notification_service.py — Centralized service for pushing events to WebSocket groups.

Uses Django Channels' channel layer to send events to both public (casino_live)
and private (player_{user_id}) groups.
"""

import logging
from typing import Any, Dict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


class NotificationService:
    """Centralized WebSocket event dispatcher."""

    @staticmethod
    def _get_layer():
        return get_channel_layer()

    # ------------------------------------------------------------------
    # Public broadcasts (casino_live group)
    # ------------------------------------------------------------------

    @staticmethod
    def broadcast_jackpot_update(amount: float) -> None:
        """Broadcast current jackpot amount to all connected clients."""
        layer = NotificationService._get_layer()
        try:
            async_to_sync(layer.group_send)(
                "casino_live",
                {
                    "type": "casino_event",
                    "event_type": "jackpot_update",
                    "message": {
                        "jackpot_amount": float(amount),
                    },
                },
            )
        except Exception as e:
            logger.error(f"Failed to broadcast jackpot update: {e}")

    @staticmethod
    def broadcast_recent_win(
        username: str, amount: float, symbol: str, is_jackpot: bool = False
    ) -> None:
        """Broadcast a recent win to all connected clients."""
        layer = NotificationService._get_layer()
        try:
            async_to_sync(layer.group_send)(
                "casino_live",
                {
                    "type": "casino_event",
                    "event_type": "recent_win",
                    "message": {
                        "username": username,
                        "amount": float(amount),
                        "symbol": symbol,
                        "is_jackpot": is_jackpot,
                    },
                },
            )
        except Exception as e:
            logger.error(f"Failed to broadcast recent win: {e}")

    # ------------------------------------------------------------------
    # Private notifications (player_{user_id} group)
    # ------------------------------------------------------------------

    @staticmethod
    def notify_player(user_id: int, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Send a private event to a specific player's WebSocket channel.

        Parameters
        ----------
        user_id : int
            The player's auth user ID.
        event_type : str
            One of: 'balance_update', 'level_up', 'bonus_awarded', 'free_spins_update'.
        payload : dict
            The event data.
        """
        layer = NotificationService._get_layer()
        group_name = f"player_{user_id}"

        try:
            async_to_sync(layer.group_send)(
                group_name,
                {
                    "type": "player_event",
                    "event_type": event_type,
                    "message": payload,
                },
            )
        except Exception as e:
            logger.error(f"Failed to notify player {user_id}: {e}")

    # ------------------------------------------------------------------
    # Convenience methods for common player notifications
    # ------------------------------------------------------------------

    @staticmethod
    def notify_balance_update(user_id: int, new_balance: float) -> None:
        """Notify a player of their updated balance."""
        NotificationService.notify_player(
            user_id,
            "balance_update",
            {"balance": float(new_balance)},
        )

    @staticmethod
    def notify_level_up(
        user_id: int, old_level: int, new_level: int,
        bonus_coins: float, free_spins: int, prize_name: str
    ) -> None:
        """Notify a player of a level-up event."""
        NotificationService.notify_player(
            user_id,
            "level_up",
            {
                "old_level": old_level,
                "new_level": new_level,
                "bonus_coins": float(bonus_coins),
                "free_spins": free_spins,
                "prize_name": prize_name,
            },
        )

    @staticmethod
    def notify_free_spins_update(user_id: int, free_spins: int) -> None:
        """Notify a player of their updated free spins count."""
        NotificationService.notify_player(
            user_id,
            "free_spins_update",
            {"free_spins": free_spins},
        )
