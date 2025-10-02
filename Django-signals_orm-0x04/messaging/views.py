#!/usr/bin/env python3 
"""
ViewSets for the chats app: Conversations and Messages.

This module enforces custom permissions so that only participants
of a conversation can view, update, or send messages.
It also implements pagination, filtering, notifications, and edit tracking.
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message, User, Notification
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .pagination import MessagePagination
from .filters import ConversationFilter, MessageFilter


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversations.
    - list: show all conversations the user is part of
    - retrieve: get details of a conversation
    - create: start a new conversation with participants
    """

    queryset = Conversation.objects.all().prefetch_related("participants", "messages")
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]

    # ✅ Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ["participants__first_name", "participants__last_name", "participants__email"]
    ordering_fields = ["created_at"]

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
    - update: edit a message (with history tracking)
    """

    queryset = Message.objects.all().select_related("sender", "receiver", "conversation")
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]

    # ✅ Enable pagination + filtering, searching, and ordering
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ["content", "sender__email"]
    ordering_fields = ["timestamp"]

    def get_queryset(self):
        """Restrict messages to conversations the user is part of."""
        user = self.request.user
        return Message.objects.filter(conversation__participants=user).select_related("sender", "receiver", "conversation")

    def create(self, request, *args, **kwargs):
        """
        Send a message in a conversation.
        Expected payload:
        {
            "conversation_id": "<uuid>",
            "receiver_id": "<uuid>",
            "content": "Hello there"
        }
        """
        conversation_id = request.data.get("conversation_id")
        receiver_id = request.data.get("receiver_id")
        content = request.data.get("content")

        if not conversation_id or not receiver_id or not content:
            return Response(
                {"error": "conversation_id, receiver_id and content are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        receiver = get_object_or_404(User, user_id=receiver_id)

        # Ensure user is a participant
        if request.user not in conversation.participants.all():
            return Response({"error": "You are not part of this conversation"}, status=status.HTTP_403_FORBIDDEN)

        # Ensure receiver is also a participant
        if receiver not in conversation.participants.all():
            return Response({"error": "Receiver must be part of the conversation"}, status=status.HTTP_400_BAD_REQUEST)

        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            conversation=conversation,
            content=content,
        )
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Edit a message.
        Expected payload:
        {
            "content": "Updated text"
        }
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Only sender can edit their own message
        if instance.sender != request.user:
            return Response({"error": "You can only edit your own messages"}, status=status.HTTP_403_FORBIDDEN)

        new_content = request.data.get("content")
        if not new_content:
            return Response({"error": "content is required"}, status=status.HTTP_400_BAD_REQUEST)

        instance.content = new_content
        instance.edited_by = request.user
        instance.save()

        serializer = self.get_serializer(instance, partial=partial)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_user(request):
    """
    Allow a user to delete their account.
    This triggers the post_delete signal to clean up related messages,
    notifications, and message histories automatically.
    """
    user = request.user
    user.delete()
    return Response({"message": "Your account and related data have been deleted."},
                    status=status.HTTP_204_NO_CONTENT)
