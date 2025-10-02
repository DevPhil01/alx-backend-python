#!/usr/bin/env python3
"""
Apps config for chats app.
Includes signal registration for notifications when a new Message is created.
"""

from django.apps import AppConfig
from django.db.models.signals import post_save


class ChatsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chats"

    def ready(self):
        from .models import Message, Notification
        import chats.signals 

        # ✅ Signal handler to create notification when new Message is created
        def create_notification(sender, instance, created, **kwargs):
            if created:
                Notification.objects.create(
                    user=instance.receiver,   # ✅ notify the receiver
                    message=instance
                )

        post_save.connect(create_notification, sender=Message)
