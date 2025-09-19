from django.db import models

# Create your models here.

from django.db import models

# Create your models here.
#!/usr/bin/env python3
"""Django models for User, Conversation, and Message"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""

    # Override the default integer ID with UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Additional fields not in AbstractUser
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    ROLE_CHOICES = [
        ("guest", "Guest"),
        ("host", "Host"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="guest")

    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=["email"]),  # extra index on email
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"


class Conversation(models.Model):
    """Model representing a conversation between users"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"Conversation {self.id} with {self.participants.count()} participants"


class Message(models.Model):
    """Model representing a message inside a conversation"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    message_body = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.sent_at}"

