from django.contrib import admin
from .models import User, Conversation, Message, Notification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "created_at")
    search_fields = ("username", "email", "role")
    list_filter = ("role", "created_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("conversation_id", "created_at")
    search_fields = ("conversation_id",)
    filter_horizontal = ("participants",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("message_id", "sender", "receiver", "conversation", "sent_at")
    search_fields = ("sender__username", "receiver__username", "message_body")
    list_filter = ("sent_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("notification_id", "user", "message", "is_read", "created_at")
    search_fields = ("user__username", "message__message_body")
    list_filter = ("is_read", "created_at")
