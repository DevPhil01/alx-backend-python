#!/usr/bin/env python3
"""
Signals for the messaging app:
- Create notification when a new message is sent
- Track message edits in history
- Cleanup user-related data on deletion
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory, User, Conversation


# 🔹 1. Auto-create notification when new message is sent
@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )


# 🔹 2. Save old content to MessageHistory before message is updated
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if not instance.pk:
        return  # new message, skip
    try:
        old_message = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return

    if old_message.content != instance.content:
        # Log old content before saving new one
        MessageHistory.objects.create(
            message=old_message,
            old_content=old_message.content,
            edited_by=instance.edited_by
        )
        instance.edited = True


# 🔹 3. Cleanup user-related data on user deletion
@receiver(post_delete, sender=User)
def cleanup_user_related_data(sender, instance, **kwargs):
    """
    After a User is deleted, ensure all their related data is cleaned up.
    """
    # Messages sent/received will be deleted automatically due to CASCADE
    # Notifications also CASCADE delete

    # But clear edit history editor references
    MessageHistory.objects.filter(edited_by=instance).update(edited_by=None)

    # Remove user from conversations (if empty, delete conversation)
    for convo in Conversation.objects.filter(participants=instance):
        convo.participants.remove(instance)
        if convo.participants.count() == 0:
            convo.delete()
