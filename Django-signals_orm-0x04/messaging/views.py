#!/usr/bin/env python3 
"""
ViewSets for the chats app: Conversations and Messages.

This module enforces custom permissions so that only participants
of a conversation can view, update, or send messages.
It also implements pagination, filtering, notifications, edit tracking, and unread message queries.
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
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
    - unread: list unread messages for the current user
    """

    queryset = Message.objects.all().select_related("sender", "conversation")
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]

    # ✅ Enable pagination + filtering, searching, and ordering
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ["message_body", "sender__email"]
    ordering_fields = ["sent_at"]

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
            "message_body": "Hello there",
            "parent_message_id": "<uuid>" (optional, for replies)
        }
        """
        conversation_id = request.data.get("conversation_id")
        message_body = request.data.get("message_body")
        parent_message_id = request.data.get("parent_message_id")

        if not conversation_id or not message_body:
            return Response(
                {"error": "conversation_id and message_body are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)

        # Ensure user is a participant
        if request.user not in conversation.participants.all():
            return Response({"error": "You are not part of this conversation"}, status=status.HTTP_403_FORBIDDEN)

        parent_message = None
        if parent_message_id:
            parent_message = get_object_or_404(Message, message_id=parent_message_id)

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=message_body,
            parent_message=parent_message
        )
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Edit a message.
        Expected payload:
        {
            "message_body": "Updated text"
        }
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Only sender can edit their own message
        if instance.sender != request.user:
            return Response({"error": "You can only edit your own messages"}, status=status.HTTP_403_FORBIDDEN)

        new_body = request.data.get("message_body")
        if not new_body:
            return Response({"error": "message_body is required"}, status=status.HTTP_400_BAD_REQUEST)

        instance.message_body = new_body
        instance.edited_by = request.user
        instance.edited = True
        instance.save()

        serializer = self.get_serializer(instance, partial=partial)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="unread")
    def unread_messages(self, request):
        """
        List unread messages for the logged-in user.
        Uses custom manager with .only() optimization.
        """
        user = request.user
        unread_qs = Message.unread.unread_for_user(user).only(
            "message_id", "message_body", "sent_at", "sender_id", "conversation_id"
        )
        page = self.paginate_queryset(unread_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(unread_qs, many=True)
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
