from celery import shared_task
from .models import Transaction

@shared_task
def process_pending_withdrawals():
    pending = Transaction.objects.filter(
        transaction_type=Transaction.TransactionType.WITHDRAW, 
        status=Transaction.TransactionStatus.PENDING
    )
    count = pending.count()
    # Mock validation and clearance
    pending.update(status=Transaction.TransactionStatus.COMPLETED)
    return f"Processed {count} withdrawals."
