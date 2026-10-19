from djang.contrib import admin

from .models import (
    Attachment,
    Conversation,
    ConversationParticipant,
    Dispute,
    Message,
    Notification,
    NotificationPreference,
    OrderDiscussion,
    SearchEvent,
    SearchIndex,
)


class ConversationParticipantInline(admin.TabularInline):
    model = ConversationParticipant
    extra = 0


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id_id", "title", "kind", "is_closed")
    inlines = (ConversationParticipantInline,)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "author", "created_at")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("file_name", "message")


@admin.register(OrderDiscussion)
class OrderDiscussionAdmin(admin.ModelAdmin):
    list_display = ("order_id", "status")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "level", "read_at")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "email_enabled", "push_enabled")


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ("subject", "opened_by", "status")


@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    list_display = ("entity_type", "entity_id", "title")


@admin.register(SearchEvent)
class SearchEventAdmin(admin.ModelAdmin):
    list_display = ("user", "query", "result_count")
