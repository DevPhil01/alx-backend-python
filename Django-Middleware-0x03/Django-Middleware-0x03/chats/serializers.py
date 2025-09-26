#!/usr/bin/env python3
"""
Serializers for the chats app: User, Conversation, and Message.
"""

from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Includes extra validation and full_name as a computed field.
    """

    # Explicit CharField for password (write-only)
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    # Computed field: combine first_name + last_name
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone_number",
            "role",
            "password",
            "created_at",
        ]
        read_only_fields = ["user_id", "created_at"]

    def get_full_name(self, obj):
        """Return first_name + last_name combined."""
        return f"{obj.first_name} {obj.last_name}".strip()

    def validate_username(self, value):
        """Ensure username has no spaces."""
        if " " in value:
            raise serializers.ValidationError("Username must not contain spaces.")
        return value

    def validate_password(self, value):
        """Custom password rule: at least 1 number."""
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        return value


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    Includes nested sender info.
    """

    sender = UserSerializer(read_only=True)

    # Example of computed preview field (first 20 chars)
    preview = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "message_id",
            "sender",
            "conversation",
            "message_body",
            "preview",
            "sent_at",
        ]
        read_only_fields = ["message_id", "sent_at"]

    def get_preview(self, obj):
        """Return first 20 chars of message_body."""
        return obj.message_body[:20] + "..." if len(obj.message_body) > 20 else obj.message_body


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    Includes nested participants and messages.
    """

    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    # Computed field: count of messages in the conversation
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "messages",
            "message_count",
            "created_at",
        ]
        read_only_fields = ["conversation_id", "created_at"]

    def get_message_count(self, obj):
        """Return total number of messages in this conversation."""
        return obj.messages.count()
