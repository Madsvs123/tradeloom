from django.contrib import admin

from .models import (
    Attachment,
    CannedResponse,
    Channel,
    Conversation,
    ConversationParticipant,
    Dispute,
    Message,
    MessageReaction,
    MessageTemplate,
    Notification,
    NotificationPreference,
    OrderDiscussion,
    ReadReceipt,
    SearchEvent,
    SearchIndex,
    Thread,
)


class ConversationParticipantInline(admin.TabularInline):
    model = ConversationParticipant
    extra = 0


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "is_private", "is_active", "owner")
    list_filter = ("kind", "is_private", "is_active")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "kind", "channel", "is_closed")
    list_filter = ("kind", "is_closed")
    inlines = (ConversationParticipantInline,)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "author", "thread", "is_system", "created_at")
    list_filter = ("is_system",)


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("title", "conversation", "status", "is_pinned", "closed_at")
    list_filter = ("status", "is_pinned")


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ("message", "user", "emoji")


@admin.register(ReadReceipt)
class ReadReceiptAdmin(admin.ModelAdmin):
    list_display = ("message", "user", "read_at")


@admin.register(CannedResponse)
class CannedResponseAdmin(admin.ModelAdmin):
    list_display = ("title", "shortcut", "owner", "is_shared", "is_active")
    list_filter = ("is_shared", "is_active")
    search_fields = ("title", "shortcut", "body")


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "channel_kind", "is_active")
    list_filter = ("channel_kind", "is_active")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("file_name", "message", "content_type")


@admin.register(OrderDiscussion)
class OrderDiscussionAdmin(admin.ModelAdmin):
    list_display = ("order_id", "status", "resolved_at")
    list_filter = ("status",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "level", "read_at")
    list_filter = ("level",)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "email_enabled", "push_enabled", "in_app_enabled", "digest_frequency")
    list_filter = ("email_enabled", "push_enabled", "digest_frequency")


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ("subject", "opened_by", "status", "resolved_at")
    list_filter = ("status",)


@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    list_display = ("entity_type", "entity_id", "title")
    search_fields = ("entity_type", "title")


@admin.register(SearchEvent)
class SearchEventAdmin(admin.ModelAdmin):
    list_display = ("user", "query", "result_count", "created_at")
