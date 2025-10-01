#!/usr/bin/env python3
"""
Unit tests for the chats app.
Covers User, Conversation, Message, and Notification functionality.
"""

from django.test import TestCase
from django.utils import timezone
from .models import User, Conversation, Message, Notification


class ChatAppTests(TestCase):
    def setUp(self):
        """Create sample users and a conversation for testing."""
        self.user1 = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="password123",
            role="guest",
        )
        self.user2 = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="password123",
            role="host",
        )

        self.conversation = Conversation.objects.create()
        self.conversation.participants.set([self.user1, self.user2])

    def test_user_creation(self):
        """Ensure users are created correctly."""
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(self.user1.username, "alice")
        self.assertEqual(self.user2.email, "bob@example.com")

    def test_conversation_creation(self):
        """Ensure conversations link participants properly."""
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertIn(self.user1, self.conversation.participants.all())
        self.assertIn(self.user2, self.conversation.participants.all())

    def test_message_and_notification(self):
        """Ensure sending a message creates a notification for the receiver."""
        msg = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            conversation=self.conversation,
            content="Hello Bob!",
            timestamp=timezone.now(),
        )

        # Message exists
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(msg.sender, self.user1)
        self.assertEqual(msg.receiver, self.user2)
        self.assertEqual(msg.content, "Hello Bob!")

        # Notification is automatically created for the receiver
        notifications = Notification.objects.filter(user=self.user2)
        self.assertEqual(notifications.count(), 1)

        notif = notifications.first()
        self.assertEqual(notif.user, self.user2)
        self.assertEqual(notif.message, msg)
        self.assertFalse(notif.is_read)
