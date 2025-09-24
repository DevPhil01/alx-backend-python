#!/usr/bin/env python3
"""
Custom permission classes for the chats app.

These permissions ensure that users can only access
their own conversations and messages.

Author: Your Name
Date: 2025-09-24
"""

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to allow only the owner of an object to access it.

    Works for models that have a `user` or `sender` field
    linking the object to a user.
    """

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "user", None) or getattr(obj, "sender", None)
        return owner == request.user


class IsConversationParticipant(permissions.BasePermission):
    """
    Permission to ensure that only participants of a conversation
    can view or modify it.

    Requires the Conversation model to have a `participants` field.
    """

    def has_object_permission(self, request, view, obj):
        participants = getattr(obj, "participants", None)
        if participants is None:
            return False
        return request.user in participants.all()


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission class to:
    - Allow only authenticated users access to the API
    - Ensure only participants in a conversation can send, view,
      update, or delete messages within it
    """

    def has_permission(self, request, view):
        # ✅ Only authenticated users can access the API
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check object-level access:
        - If the object is a Conversation, user must be a participant
        - If the object is a Message, user must be part of the related conversation
        """
        from .models import Conversation, Message

        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()

        if isinstance(obj, Message):
            return request.user in obj.conversation.participants.all()

        return False


class ReadOnly(permissions.BasePermission):
    """
    Permission class that allows read-only access to all requests,
    but restricts modifications to authenticated users only.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
