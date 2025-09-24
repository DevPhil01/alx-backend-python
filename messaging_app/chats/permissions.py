#!/usr/bin/env python3
"""
Custom permissions for the chats app.

This file defines object-level permissions to ensure that only users
who are authenticated and participants of a conversation can access or modify it.

Supports:
- Safe methods: GET, HEAD, OPTIONS
- Write methods: POST, PUT, PATCH, DELETE
"""

from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only authenticated participants of a conversation
    to view, send, update, or delete messages.
    """

    def has_permission(self, request, view):
        """
        Global check: user must be authenticated first.
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level check: user must be a participant of the conversation.
        """

        # Ensure only authenticated users proceed
        if not request.user or not request.user.is_authenticated:
            return False

        # Only participants of the conversation can interact
        if request.user in obj.participants.all():
            # SAFE_METHODS = GET, HEAD, OPTIONS
            if request.method in permissions.SAFE_METHODS:
                return True

            # Explicitly allow write/unsafe methods
            if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                return True

        # Deny access otherwise
        return False
