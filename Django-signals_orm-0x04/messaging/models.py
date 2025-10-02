#!/usr/bin/env python3
"""
Models for the chats app: User, Conversation, Message, MessageHistory, and Notification.
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds fields from the schema specification.
    """

    # Override the default `id` with UUID
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )

    email = models.EmailField(
        unique=True,
        null=False,
        blank=False
    )

    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    ROLE_CHOICES = [
        ("guest", "Guest"),
        ("host", "Host"),
        ("admin", "Admin"),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        null=False,
        blank=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    def __str__(self):
        return f"{self.username} ({self.email})"


class Conversation(models.Model):
    """
    Conversation model that tracks which users are involved in a conversation.
    """

    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )

    participants = models.ManyToManyField(
        User,
        related_name="conversations"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class UnreadMessagesManager(models.Manager):
    """
    Custom manager to filter unread messages for a given user.
    Optimized with `.only()` to fetch minimal fields.
    """

    def for_user(self, user):
        return (
            self.get_queryset()
            .filter(conversation__participants=user, read=False)
            .only("message_id", "sender", "message_body", "sent_at", "conversation")
            .select_related("sender", "conversation")
        )


class Message(models.Model):
    """
    Message model containing the sender, conversation, and message body.
    Supports threaded replies via parent_message and edit history.
    """

    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    message_body = models.TextField(null=False, blank=False)

    sent_at = models.DateTimeField(auto_now_add=True)

    # ✅ NEW: Threaded replies
    parent_message = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies"
    )

    # ✅ Track edits
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="edited_messages"
    )

    # ✅ NEW: Track read/unread status
    read = models.BooleanField(default=False)

    # ✅ Attach the custom unread manager
    objects = models.Manager()  # default manager
    unread = UnreadMessagesManager()  # custom manager

    def __str__(self):
        return f"Message {self.message_id} from {self.sender.username}"

    def get_thread(self):
        """
        Recursively fetch all replies to this message (threaded).
        Returns a nested structure of messages.
        """
        replies = self.replies.all().select_related("sender").prefetch_related("replies")
        return [
            {
                "id": reply.message_id,
                "sender": reply.sender.username,
                "content": reply.message_body,
                "sent_at": reply.sent_at,
                "replies": reply.get_thread()
            }
            for reply in replies
        ]


class MessageHistory(models.Model):
    """
    Stores previous versions of edited messages.
    """

    history_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="history"
    )

    old_content = models.TextField()

    edited_at = models.DateTimeField(auto_now_add=True)

    edited_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="edit_histories"
    )

    def __str__(self):
        return f"History for Message {self.message.message_id} at {self.edited_at}"


class Notification(models.Model):
    """
    Notifications for users when they receive new messages.
    """

    notification_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} about message {self.message.message_id}"
