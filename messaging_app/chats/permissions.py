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


class ReadOnly(permissions.BasePermission):
    """
    Permission class that allows read-only access to all requests,
    but restricts modifications to authenticated users only.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
