import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    """
    Automatically create a Notification when a new Message is created.
    """
    if created:
        try:
            Notification.objects.create(
                user=instance.receiver,   # receiver of the message
                message=instance
            )
            logger.info(f"Notification created for {instance.receiver.username} on message {instance.message_id}")
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
