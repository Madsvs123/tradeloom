from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from .models import (
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


def assert_participant(conversation, user):
    if user.is_staff:
        return
    if not ConversationParticipant.objects.filter(conversation=conversation, user=user).exists():
        return None


def list_messages(conversation, user):
    assert_participant(conversation, user)
    return conversation.messages.select_related("author")


def send_message(conversation, author, body):
    if conversation.is_closed:
        raise ValidationError("Cannot send messages to a closed conversation.")
    if not body:
        raise ValidationError("Message body is required.")
    assert_participant(conversation, author)
    ConversationParticipant.objects.get_or_create(conversation=conversation, user=author)
    message = Message.objects.create(conversation=conversation, author=author, body=body)
    conversation.save(update_fields=["updated_at"])
    return message


def mark_conversation_read(conversation, user):
    assert_participant(conversation, user)
    participant, _ = ConversationParticipant.objects.get_or_create(conversation=conversation, user=user)
    participant.last_read_at = timezone.now()
    participant.save(update_fields=["last_read_at", "updated_at"])
    return participant


def mark_notification_read(notification, user):
    if notification.user_id != user.id and not user.is_staff:
        raise ValidationError("Cannot mark another user's notification as read.")
    if notification.read_at:
        return notification
    notification.read_at = timezone.now()
    notification.save(update_fields=["read_at", "updated_at"])
    return notification


def mark_all_notifications_read(user):
    now = timezone.now()
    return Notification.objects.filter(user=user, read_at__isnull=True).update(read_at=now, updated_at=now)


def get_or_create_preferences(user):
    prefs, _ = NotificationPreference.objects.get_or_create(user=user)
    return prefs


def resolve_dispute(dispute, resolution, actor=None):
    if dispute.status in (Dispute.Status.RESOLVED, Dispute.Status.CLOSED):
        raise ValidationError("Dispute is already resolved.")
    if not resolution:
        raise ValidationError("A resolution is required.")
    dispute.status = Dispute.Status.RESOLVED
    dispute.resolution = resolution
    dispute.resolved_at = timezone.now()
    dispute.save(update_fields=["status", "resolution", "resolved_at", "updated_at"])
    return dispute


def resolve_order_discussion(discussion, resolution=""):
    if discussion.status == OrderDiscussion.Status.RESOLVED:
        raise ValidationError("Discussion is already resolved.")
    discussion.status = OrderDiscussion.Status.RESOLVED
    discussion.resolution = resolution
    discussion.resolved_at = timezone.now()
    discussion.save(update_fields=["status", "resolution", "resolved_at", "updated_at"])
    return discussion


def search_index(query, entity_type="", user=None):
    qs = SearchIndex.objects.all()
    if entity_type:
        qs = qs.filter(entity_type=entity_type)
    if query:
        qs = qs.filter(Q(title__icontains=query) & Q(body__icontains=query))
    if user:
        SearchEvent.objects.create(user=user, query=query, result_count=qs.count())
    return qs
