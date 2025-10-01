#!/usr/bin/env python3
"""
Admin configuration for the chats app.
Registers User, Conversation, Message, and Notification models.
"""

from django.contrib import admin
from .models import User, Conversation, Message, Notification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "phone_number", "created_at")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("role", "created_at")
    ordering = ("-created_at",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("conversation_id", "created_at")
    search_fields = ("conversation_id",)
    filter_horizontal = ("participants",)
    ordering = ("-created_at",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("message_id", "sender", "receiver", "conversation", "content", "timestamp")
    search_fields = ("content", "sender__username", "receiver__username")
    list_filter = ("timestamp",)
    ordering = ("-timestamp",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "message", "is_read", "created_at")
    search_fields = ("user__username", "message__content")
    list_filter = ("is_read", "created_at")
    ordering = ("-created_at",)
