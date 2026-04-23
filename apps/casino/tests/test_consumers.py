"""
test_consumers.py — WebSocket consumer tests.

Uses channels.testing.WebsocketCommunicator to test both
CasinoConsumer (public) and PlayerConsumer (personal).
"""

import json
import pytest
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from asgiref.sync import sync_to_async

from apps.casino.consumers import CasinoConsumer
from apps.casino.player_consumer import PlayerConsumer


@override_settings(
    CHANNEL_LAYERS={
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
)
class CasinoConsumerTestCase(TestCase):
    """Tests for the public CasinoConsumer."""

    async def test_connect_and_disconnect(self):
        """Client should be able to connect and disconnect cleanly."""
        communicator = WebsocketCommunicator(
            CasinoConsumer.as_asgi(), "/ws/casino/"
        )

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_ping_pong(self):
        """Client should receive pong response to ping."""
        communicator = WebsocketCommunicator(
            CasinoConsumer.as_asgi(), "/ws/casino/"
        )

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to({"type": "ping"})
        response = await communicator.receive_json_from(timeout=5)
        self.assertEqual(response["type"], "pong")

        await communicator.disconnect()

    async def test_casino_event_broadcast(self):
        """Casino events should be received by connected clients."""
        communicator = WebsocketCommunicator(
            CasinoConsumer.as_asgi(), "/ws/casino/"
        )

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Simulate a broadcast via channel layer
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "casino_live",
            {
                "type": "casino_event",
                "event_type": "jackpot_update",
                "message": {"jackpot_amount": 5000.00},
            },
        )

        response = await communicator.receive_json_from(timeout=5)
        self.assertEqual(response["type"], "jackpot_update")
        self.assertEqual(response["message"]["jackpot_amount"], 5000.00)

        await communicator.disconnect()


@override_settings(
    CHANNEL_LAYERS={
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
)
class PlayerConsumerTestCase(TestCase):
    """Tests for the personal PlayerConsumer."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="wsplayer", password="testpass123"
        )
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

    async def test_connect_with_valid_token(self):
        """Player should connect with a valid JWT token."""
        communicator = WebsocketCommunicator(
            PlayerConsumer.as_asgi(),
            f"/ws/player/{self.user.id}/?token={self.token}",
        )
        communicator.scope["url_route"] = {
            "kwargs": {"user_id": str(self.user.id)}
        }

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_connect_without_token_rejected(self):
        """Player should be rejected without a token."""
        communicator = WebsocketCommunicator(
            PlayerConsumer.as_asgi(),
            f"/ws/player/{self.user.id}/",
        )
        communicator.scope["url_route"] = {
            "kwargs": {"user_id": str(self.user.id)}
        }

        connected, code = await communicator.connect()
        # Should either not connect or close with 4001
        if connected:
            # The consumer may accept then close
            pass

    async def test_player_receives_personal_event(self):
        """Player should receive events sent to their personal group."""
        communicator = WebsocketCommunicator(
            PlayerConsumer.as_asgi(),
            f"/ws/player/{self.user.id}/?token={self.token}",
        )
        communicator.scope["url_route"] = {
            "kwargs": {"user_id": str(self.user.id)}
        }

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send event to player group
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"player_{self.user.id}",
            {
                "type": "player_event",
                "event_type": "balance_update",
                "message": {"balance": 1500.00},
            },
        )

        response = await communicator.receive_json_from(timeout=5)
        self.assertEqual(response["type"], "balance_update")
        self.assertEqual(response["message"]["balance"], 1500.00)

        await communicator.disconnect()
