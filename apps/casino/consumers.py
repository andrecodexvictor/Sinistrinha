"""
consumers.py — WebSocket consumers for real-time casino events.

Supports two channel groups:
- casino_live: public feed of big wins (all connected clients)
- user_{id}: private channel for balance/level updates
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class CasinoConsumer(AsyncWebsocketConsumer):
    """Public casino feed — big wins, jackpot updates."""

    async def connect(self):
        self.room_group_name = 'casino_live'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data):
        # Public channel is read-only for clients
        pass

    async def casino_event(self, event):
        """Send event to WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': event.get('event_type', 'update'),
            'message': event.get('message', {}),
        }))


class UserConsumer(AsyncWebsocketConsumer):
    """
    Private per-user channel for balance updates, level-ups, etc.
    Connect at: ws://host/ws/user/{user_id}/
    """

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'user_{self.user_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data):
        # User channel is server-push only
        pass

    async def casino_event(self, event):
        """Send private event to user's WebSocket."""
        await self.send(text_data=json.dumps({
            'type': event.get('event_type', 'update'),
            'message': event.get('message', {}),
        }))
