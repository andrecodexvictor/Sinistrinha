import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinistrinha.settings.prod')

app = Celery('sinistrinha')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat schedule — periodic tasks
app.conf.beat_schedule = {
    'broadcast-jackpot-ticker': {
        'task': 'apps.game.tasks.broadcast_jackpot_ticker',
        'schedule': 5.0,  # Every 5 seconds
    },
    'snapshot-jackpot-hourly': {
        'task': 'apps.game.tasks.snapshot_jackpot',
        'schedule': crontab(minute=0),  # Every hour on the hour
    },
    'process-pending-withdrawals': {
        'task': 'apps.payments.tasks.process_pending_withdrawals',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}

