#!/usr/bin/env python3
"""
Custom permissions for the chats app.

This file defines object-level permissions to ensure that only users
who are participants of a conversation can access or modify it.

Supports:
- Safe methods: GET, HEAD, OPTIONS
- Write methods: POST, PUT, PATCH, DELETE
"""

from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only participants of a conversation
    to view or modify it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check.
        Ensures the requesting user is part of the conversation.

        Args:
            request: The HTTP request instance.
            view: The DRF view where the permission is applied.
            obj: The object (Conversation) being accessed.

        Returns:
            bool: True if the user is allowed, False otherwise.
        """

        # Only participants of the conversation can interact
        if request.user in obj.participants.all():
            # SAFE_METHODS = GET, HEAD, OPTIONS
            if request.method in permissions.SAFE_METHODS:
                return True

            # Explicitly handle write/unsafe methods
            if request.method in ["PUT", "PATCH", "DELETE", "POST"]:
                return True

        # Deny access if user is not a participant
        return False
