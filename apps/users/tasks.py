from celery import shared_task
from django.contrib.auth.models import User

@shared_task
def send_welcome_email(user_id):
    try:
        user = User.objects.get(id=user_id)
        # Mock email dispatching
        return f"Welcome email sent to {user.email}"
    except User.DoesNotExist:
        return "User not found"
