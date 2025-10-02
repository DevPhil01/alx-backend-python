#!/usr/bin/env python3
"""
Models for the chats/messaging app: User, Conversation, Message, MessageHistory, and Notification.
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

    # Already exist in AbstractUser: first_name, last_name, password, email, username
    # We override email to make it unique and required.
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


class Message(models.Model):
    """
    Message model containing the sender, receiver, conversation, and message body.
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
        related_name="messages_sent"
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messages_received"
    )

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    content = models.TextField(null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Edit tracking
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages_edited"
    )

    def __str__(self):
        return f"Message {self.message_id} from {self.sender.username}"


class MessageHistory(models.Model):
    """
    Stores previous versions of messages when edited.
    """

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="history"
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="message_histories"
    )

    def __str__(self):
        return f"History of {self.message.message_id} at {self.edited_at}"


class Notification(models.Model):
    """
    Notification model to alert users when they receive new messages.
    """

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
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} about {self.message.message_id}"


class Meta:
    app_label = "chats"
