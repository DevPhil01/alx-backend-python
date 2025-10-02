#!/usr/bin/env python3
"""
Custom managers for the messaging app.
Includes UnreadMessagesManager to filter unread messages for a user.
"""

from django.db import models


class UnreadMessagesManager(models.Manager):
    """
    Custom manager for unread messages.
    Provides a helper method to get all unread messages for a given user.
    """

    def unread_for_user(self, user):
        """
        Return unread messages for a specific user.
        Uses `.only()` for query optimization.
        """
        return self.filter(
            conversation__participants=user,
            read=False
        ).only("message_id", "sender", "message_body", "sent_at", "conversation")
