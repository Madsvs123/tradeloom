from rest_framework import serializers

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


def make(model, extra=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


ChannelSerializer = make(Channel)


class MessageSerializer(serializers.ModelSerializer):
    reactions = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = ("id", "author", "created_at", "updated_at")

    def get_reactions(self, obj):
        reactions = obj.reactions.values("emoji").order_by("emoji").distinct()
        return [
            {"emoji": reaction["emoji"], "count": obj.reactions.filter(emoji=reaction["emoji"]).count()}
            for reaction in reactions
        ]


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


ThreadSerializer = make(Thread, extra=("status", "closed_by", "closed_at"))
MessageReactionSerializer = make(MessageReaction)
ReadReceiptSerializer = make(ReadReceipt)
CannedResponseSerializer = make(CannedResponse)
MessageTemplateSerializer = make(MessageTemplate)
AttachmentSerializer = make(Attachment)
OrderDiscussionSerializer = make(OrderDiscussion, extra=("status", "resolved_at"))


class NotificationSerializer(serializers.ModelSerializer):
    is_read = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


NotificationPreferenceSerializer = make(NotificationPreference, extra=("user",))
DisputeSerializer = make(Dispute, extra=("status", "resolved_at", "opened_by"))
SearchIndexSerializer = make(SearchIndex)
SearchEventSerializer = make(SearchEvent, extra=("user", "result_count"))


class ConversationDetailSerializer(ConversationSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    threads = ThreadSerializer(many=True, read_only=True)

    class Meta(ConversationSerializer.Meta):
        fields = "__all__"
        read_only_fields = ConversationSerializer.Meta.read_only_fields
