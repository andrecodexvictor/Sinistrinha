"""
supabase_client.py — Thin wrapper around the Supabase Python client.

Provides a singleton client initialized from environment variables and
helper methods for Supabase Realtime broadcasting.
"""

import logging
from functools import lru_cache
from typing import Any, Dict, Optional

from django.conf import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_client():
    """
    Return a cached Supabase client instance.

    Requires SUPABASE_URL and SUPABASE_KEY (or SUPABASE_SERVICE_ROLE_KEY)
    to be set in Django settings / environment.
    """
    try:
        from supabase import create_client, Client
    except ImportError:
        logger.warning(
            "supabase-py is not installed. Supabase client will not be available. "
            "Install with: pip install supabase"
        )
        return None

    url = getattr(settings, 'SUPABASE_URL', None)
    key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', None) or getattr(
        settings, 'SUPABASE_KEY', None
    )

    if not url or not key:
        logger.warning(
            "SUPABASE_URL or SUPABASE_KEY is not configured. "
            "Supabase client will not be available."
        )
        return None

    client: Client = create_client(url, key)
    return client


def broadcast_realtime(
    channel: str,
    event: str,
    payload: Dict[str, Any],
) -> bool:
    """
    Broadcast a message via Supabase Realtime (optional complement to Channels).

    Parameters
    ----------
    channel : str
        The Supabase Realtime channel name (e.g. 'casino_live').
    event : str
        The event type (e.g. 'jackpot_update', 'recent_win').
    payload : dict
        The data to broadcast.

    Returns
    -------
    bool
        True if broadcast succeeded, False otherwise.
    """
    client = get_client()
    if client is None:
        logger.debug("Supabase client unavailable; skipping realtime broadcast.")
        return False

    try:
        channel_instance = client.realtime.channel(channel)
        channel_instance.send_broadcast(event, payload)
        logger.info(f"Broadcast sent: channel={channel}, event={event}")
        return True
    except Exception as e:
        logger.error(f"Supabase Realtime broadcast failed: {e}")
        return False
