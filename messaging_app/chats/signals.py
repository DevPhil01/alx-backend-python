from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    """
    Signal: Trigger a notification when a new message is created.
    """
    if created:
        Notification.objects.create(
            user=instance.receiver,  # notify the receiver
            message=instance
        )
