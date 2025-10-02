#!/usr/bin/env python3
"""
Signals for the messaging app.
- Create notifications when new messages are sent
- Save message history when a message is edited
- Cleanup user-related data on user deletion
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory, User


@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    """
    When a new message is created, automatically create a notification
    for the receiving user(s).
    """
    if created:
        conversation = instance.conversation
        # Notify all participants except the sender
        for participant in conversation.participants.exclude(user_id=instance.sender.user_id):
            Notification.objects.create(
                user=participant,
                message=instance,
                is_read=False,
            )


@receiver(pre_save, sender=Message)
def save_message_history_before_edit(sender, instance, **kwargs):
    """
    Before a message is updated, log its old content into MessageHistory.
    """
    if instance.pk:  # Editing an existing message
        try:
            old_message = Message.objects.get(pk=instance.pk)  # ✅ Explicit queryset
            if old_message.message_body != instance.message_body:
                MessageHistory.objects.create(
                    message=old_message,
                    old_content=old_message.message_body,
                    edited_by=old_message.sender,
                )
                instance.edited = True
        except Message.DoesNotExist:
            pass


@receiver(post_delete, sender=User)
def cleanup_user_related_data(sender, instance, **kwargs):
    """
    Cleanup all related data when a user account is deleted:
    - Delete all messages by the user
    - Delete all notifications for the user
    - Delete all message histories created by the user
    """
    # ✅ Explicit queryset filters
    Message.objects.filter(sender=instance).delete()
    Notification.objects.filter(user=instance).delete()
    MessageHistory.objects.filter(edited_by=instance).delete()
