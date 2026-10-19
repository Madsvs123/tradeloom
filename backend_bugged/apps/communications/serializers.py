from rest_framewrk import serializers

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


def make(model, extra=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
        return Auto


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = ("id", "author", "created_at", "updated_at")


class ConversationParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationParticipant
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ConversationSerializer(serializers.ModelSerializer):
    participants = ConversationParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = "__all__"
        read_only_fields = ("id", "created_by", "created_at", "updated_at")


AttachmentSerializer = make(Attachment)
OrderDiscussionSerializer = make(OrderDiscussion, extra=("status", "resolved_at"))


class NotificationSerializer(serializers.ModelSerializer):
    is_read = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("id", "user", "read_at", "created_at", "updated_at")


NotificationPreferenceSerializer = make(NotificationPreference, extra=("user",))
DisputeSerializer = make(Dispute, extra=("status", "resolved_at", "opened_by"))
SearchIndexSerializer = make(SearchIndex)
SearchEventSerializer = make(SearchEvent, extra=("user", "result_count"))
