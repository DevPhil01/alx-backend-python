#!/usr/bin/env python3
"""
ViewSets for the chats app: Conversations and Messages.

This module enforces custom permissions so that only participants
of a conversation can view, update, or send messages.
It also implements pagination, filtering, notifications, and edit tracking.
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .pagination import MessagePagination
from .filters import ConversationFilter, MessageFilter


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversations.
    """

    queryset = Conversation.objects.all().prefetch_related("participants", "messages")
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ["participants__first_name", "participants__last_name", "participants__email"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(participants=user).prefetch_related("participants", "messages")

    def create(self, request, *args, **kwargs):
        participants_ids = request.data.get("participants", [])
        if not participants_ids:
            return Response({"error": "Participants are required"}, status=status.HTTP_400_BAD_REQUEST)

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
    """

    queryset = Message.objects.all().select_related("sender", "conversation")
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]

    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ["message_body", "sender__email"]
    ordering_fields = ["sent_at"]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(conversation__participants=user).select_related("sender", "conversation")

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get("conversation_id")
        content = request.data.get("content")

        if not conversation_id or not content:
            return Response(
                {"error": "conversation_id and content are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)

        if request.user not in conversation.participants.all():
            return Response({"error": "You are not part of this conversation"}, status=status.HTTP_403_FORBIDDEN)

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=content,
        )
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        if instance.sender != request.user:
            return Response({"error": "You can only edit your own messages"}, status=status.HTTP_403_FORBIDDEN)

        new_content = request.data.get("content")
        if not new_content:
            return Response({"error": "content is required"}, status=status.HTTP_400_BAD_REQUEST)

        instance.message_body = new_content
        instance.edited_by = request.user
        instance.edited = True
        instance.save()

        serializer = self.get_serializer(instance, partial=partial)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="unread")
    def list_unread(self, request, *args, **kwargs):
        """
        List unread messages for the logged-in user.
        """
        user = request.user
        unread_messages = Message.unread.unread_for_user(user).only(
            "message_id", "sender", "message_body", "sent_at", "conversation"
        )
        page = self.paginate_queryset(unread_messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(unread_messages, many=True)
        return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_user(request):
    """
    Allow a user to delete their account.
    """
    user = request.user
    user.delete()
    return Response({"message": "Your account and related data have been deleted."},
                    status=status.HTTP_204_NO_CONTENT)
