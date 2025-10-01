from django.test import TestCase
from django.utils import timezone
from .models import User, Conversation, Message, Notification
import uuid


class MessagingAppTests(TestCase):

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="password123",
            role="guest"
        )
        self.user2 = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="password123",
            role="host"
        )

        # Create a conversation
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def test_create_message_and_notification(self):
        # Send a message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            conversation=self.conversation,
            message_body="Hello Bob!"
        )

        # Check message was created
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)

        # Check notification was auto-created
        notifications = Notification.objects.filter(user=self.user2)
        self.assertEqual(notifications.count(), 1)
        self.assertEqual(notifications.first().message, message)

    def test_multiple_messages(self):
        # Send multiple messages
        for i in range(3):
            Message.objects.create(
                sender=self.user1,
                receiver=self.user2,
                conversation=self.conversation,
                message_body=f"Test message {i}"
            )

        self.assertEqual(Message.objects.count(), 3)
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 3)
