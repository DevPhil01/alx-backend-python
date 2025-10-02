"""
Signals for the chats app.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Message, Notification, MessageHistory


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    """Create a notification when a new message is sent."""
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Before a message is saved, if it's being updated (not created),
    save its old content into MessageHistory.
    """
    if not instance._state.adding:  # means it's an update, not a new message
        try:
            old_instance = Message.objects.get(pk=instance.pk)
            if old_instance.content != instance.content:
                # Mark message as edited
                instance.edited = True

                # Save old content to history
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_instance.content,
                    edited_at=timezone.now(),
                    edited_by=instance.edited_by  # track who made the edit
                )
        except Message.DoesNotExist:
            pass
