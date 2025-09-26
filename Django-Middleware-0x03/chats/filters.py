#!/usr/bin/env python3
"""
Custom filter classes for the chats app.

This module uses django-filters to provide advanced filtering
capabilities for messages and conversations.
"""

import django_filters
from .models import Message, Conversation


class MessageFilter(django_filters.FilterSet):
    """
    Filter messages by:
    - sender: filter by sender's user_id
    - conversation: filter by conversation_id
    - date range: filter by messages sent between two dates
    """

    sender = django_filters.UUIDFilter(field_name="sender__user_id", lookup_expr="exact")
    conversation = django_filters.UUIDFilter(field_name="conversation__conversation_id", lookup_expr="exact")
    sent_after = django_filters.DateTimeFilter(field_name="sent_at", lookup_expr="gte")
    sent_before = django_filters.DateTimeFilter(field_name="sent_at", lookup_expr="lte")

    class Meta:
        model = Message
        fields = ["sender", "conversation", "sent_after", "sent_before"]


class ConversationFilter(django_filters.FilterSet):
    """
    Filter conversations by:
    - participant: show conversations containing a specific user
    - created date range
    """

    participant = django_filters.UUIDFilter(field_name="participants__user_id", lookup_expr="exact")
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Conversation
        fields = ["participant", "created_after", "created_before"]
