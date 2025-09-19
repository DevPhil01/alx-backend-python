from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

# Create your views here.
#!/usr/bin/env python3
"""
ViewSets for the chats app: Conversations and Messages.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversations.
    - list: show all conversations the user is part of
    - retrieve: get details of a conversation
    - create: start a new conversation with participants
    """

    queryset = Conversation.objects.all().prefetch_related("participants", "messages")
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter conversations to only those involving the logged-in user."""
        user = self.request.user
        return Conversation.objects.filter(participants=user).prefetch_related("participants", "messages")

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation.
        Expected payload:
        {
            "participants": [user_id1, user_id2, ...]
        }
        """
        participants_ids = request.data.get("participants", [])
        if not participants_ids:
            return Response({"error": "Participants are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Always include the logged-in user
        participants_ids.append(str(request.user.user_id))
        participants = User.objects.filter(user_id__in=participants_ids).distinct()

        if participants.count() < 2:
            return Response({"error": "At least two unique participants required"}, status=status.HTTP_400_BAD_REQUEST)

        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Messages.
    - list: show all messages in a conversation
    - retrieve: get a single message
    - create: send a new message in a conversation
    """

    queryset = Message.objects.all().select_related("sender", "conversation")
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Restrict messages to conversations the user is part of."""
        user = self.request.user
        return Message.objects.filter(conversation__participants=user).select_related("sender", "conversation")

    def create(self, request, *args, **kwargs):
        """
        Send a message in a conversation.
        Expected payload:
        {
            "conversation_id": "<uuid>",
            "message_body": "Hello there"
        }
        """
        conversation_id = request.data.get("conversation_id")
        message_body = request.data.get("message_body")

        if not conversation_id or not message_body:
            return Response({"error": "conversation_id and message_body are required"}, status=status.HTTP_400_BAD_REQUEST)

        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)

        # Ensure user is a participant
        if request.user not in conversation.participants.all():
            return Response({"error": "You are not part of this conversation"}, status=status.HTTP_403_FORBIDDEN)

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=message_body,
        )
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
