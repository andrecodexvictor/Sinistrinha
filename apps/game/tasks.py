"""
tasks.py — Celery tasks for the game app.

Includes jackpot ticker broadcast (Celery Beat) and probability edge updates.
"""

from celery import shared_task
from .models import JackpotPool


@shared_task
def update_probability_edge(new_edge):
    """Simulate API call to/from the probability agent."""
    return f"Edge updated to {new_edge}"


@shared_task
def snapshot_jackpot():
    """Take a snapshot of the current jackpot pool for auditing."""
    try:
        pool = JackpotPool.objects.get(id=1)
        return f"Snapshot taken: {pool.current_amount}"
    except JackpotPool.DoesNotExist:
        return "No jackpot pool to snapshot"


@shared_task
def broadcast_jackpot_ticker():
    """
    Periodic task (Celery Beat) that broadcasts the current jackpot
    to all connected WebSocket clients every few seconds.
    """
    from apps.game.services.notification_service import NotificationService

    try:
        pool = JackpotPool.objects.get(id=1)
        NotificationService.broadcast_jackpot_update(float(pool.current_amount))
        return f"Jackpot ticker broadcast: {pool.current_amount}"
    except JackpotPool.DoesNotExist:
        return "No jackpot pool to broadcast"
