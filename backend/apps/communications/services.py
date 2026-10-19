from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from .models import (
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

THREAD_TRANSITIONS = {
    Thread.Status.OPEN: {Thread.Status.CLOSED},
    Thread.Status.CLOSED: set(),
}


def _assert_thread_transition(current, target):
    allowed = THREAD_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ValidationError(f"Cannot move thread from status '{current}' to '{target}'.")


def assert_participant(conversation, user):
    if user.is_staff:
        return
    if not ConversationParticipant.objects.filter(conversation=conversation, user=user).exists():
        raise ValidationError("You are not a participant of this conversation.")


def list_messages(conversation, user):
    assert_participant(conversation, user)
    return conversation.messages.select_related("author")


def send_message(conversation, author, body):
    if conversation.is_closed:
        raise ValidationError("Cannot send messages to a closed conversation.")
    if not body:
        raise ValidationError("Message body is required.")
    assert_participant(conversation, author)
    message = Message.objects.create(conversation=conversation, author=author, body=body)
    conversation.save(update_fields=["updated_at"])
    return message


def send_message_from_template(conversation, author, template_id, variables=None):
    if conversation.is_closed:
        raise ValidationError("Cannot send messages to a closed conversation.")
    try:
        template = MessageTemplate.objects.get(pk=template_id, is_active=True)
    except MessageTemplate.DoesNotExist:
        raise ValidationError("Active message template not found.")
    assert_participant(conversation, author)
    variables = variables or {}
    body = template.body
    for key, value in variables.items():
        body = body.replace("{{" + key + "}}", str(value))
    return Message.objects.create(conversation=conversation, author=author, body=body, is_system=True)


def mark_conversation_read(conversation, user):
    assert_participant(conversation, user)
    participant, _ = ConversationParticipant.objects.get_or_create(conversation=conversation, user=user)
    participant.last_read_at = timezone.now()
    participant.save(update_fields=["last_read_at", "updated_at"])
    unseen = conversation.messages.filter(author=user).exclude(read_receipts__user=user)
    ReadReceipt.objects.bulk_create(
        [ReadReceipt(message=message, user=user) for message in unseen[:500]]
    )
    return participant


def mark_message_read(message, user):
    assert_participant(message.conversation, user)
    receipt, _ = ReadReceipt.objects.get_or_create(message=message, user=user)
    return receipt


def toggle_reaction(message, user, emoji):
    if not emoji:
        raise ValidationError("An emoji is required.")
    assert_participant(message.conversation, user)
    reaction, created = MessageReaction.objects.get_or_create(message=message, user=user, emoji=emoji)
    if not created:
        reaction.delete()
        return None
    return reaction


def close_thread(thread, user=None):
    _assert_thread_transition(thread.status, Thread.Status.CLOSED)
    thread.status = Thread.Status.CLOSED
    thread.closed_by = user
    thread.closed_at = timezone.now()
    thread.save(update_fields=["status", "closed_by", "closed_at", "updated_at"])
    return thread


def pin_thread(thread):
    thread.is_pinned = True
    thread.save(update_fields=["is_pinned", "updated_at"])
    return thread


def unpin_thread(thread):
    thread.is_pinned = False
    thread.save(update_fields=["is_pinned", "updated_at"])
    return thread


def set_channel_active(channel, active):
    if active == channel.is_active:
        raise ValidationError(f"Channel is already {'active' if active else 'inactive'}.")
    channel.is_active = active
    channel.save(update_fields=["is_active", "updated_at"])
    return channel


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
        qs = qs.filter(Q(title__icontains=query) | Q(body__icontains=query))
    if user:
        SearchEvent.objects.create(user=user, query=query, result_count=qs.count())
    return qs
