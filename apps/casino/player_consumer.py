"""
player_consumer.py — Personal WebSocket consumer for authenticated players.

Each authenticated player joins a private group `player_{user_id}` and
receives personal events: balance updates, level-ups, bonuses, free spins.
"""

import json
import logging
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class PlayerConsumer(AsyncWebsocketConsumer):
    """Personal WebSocket consumer for a single authenticated player."""

    async def connect(self):
        # Extract user_id from URL route
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f"player_{self.user_id}"

        # Validate JWT token from query string
        query_string = self.scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]

        if not await self._authenticate(token):
            await self.close(code=4001)
            return

        # Join personal group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()
        logger.info(f"Player {self.user_id} connected to personal channel")

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )
            logger.info(f"Player {self.user_id} disconnected from personal channel")

    async def receive(self, text_data):
        """Handle incoming messages from the player (e.g., heartbeat, ping)."""
        try:
            data = json.loads(text_data)
            msg_type = data.get("type", "")

            if msg_type == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))
        except json.JSONDecodeError:
            pass

    # ------------------------------------------------------------------
    # Event handlers (called by channel layer group_send)
    # ------------------------------------------------------------------

    async def player_event(self, event):
        """
        Handle a player-specific event dispatched by NotificationService.

        Expected event structure:
            {
                "type": "player_event",
                "event_type": "balance_update" | "level_up" | "bonus_awarded" | "free_spins_update",
                "message": { ... }
            }
        """
        await self.send(text_data=json.dumps({
            "type": event.get("event_type", "update"),
            "data": event.get("message", {}),
        }))

    # ------------------------------------------------------------------
    # Authentication helper
    # ------------------------------------------------------------------

    @database_sync_to_async
    def _authenticate(self, token: str) -> bool:
        """
        Validate a JWT access token and check the user_id matches the URL.

        Returns True if authentication succeeds.
        """
        if not token:
            logger.warning(f"No token provided for player {self.user_id}")
            return False

        try:
            access_token = AccessToken(token)
            token_user_id = str(access_token["user_id"])

            if token_user_id != str(self.user_id):
                logger.warning(
                    f"Token user_id {token_user_id} doesn't match URL user_id {self.user_id}"
                )
                return False

            # Verify user exists
            user = User.objects.filter(id=token_user_id).first()
            if not user:
                logger.warning(f"User {token_user_id} not found")
                return False

            self.scope["user"] = user
            return True

        except Exception as e:
            logger.warning(f"JWT authentication failed for player {self.user_id}: {e}")
            return False
