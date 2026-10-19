from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from .models import (
    Conversation,
    ConversationParticipant,
    Dispute,
    Message,
    MessageReaction,
    Notification,
    SearchEvent,
    SearchIndex,
)
from .services import (
    close_thread,
    mark_notification_read,
    resolve_dispute,
    send_message,
    toggle_reaction,
)


class CommunicationsModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.buyer = User.objects.create_user(username="buyer", password="pass")
        self.vendor = User.objects.create_user(username="vendor", password="pass")

    def test_send_message_records_author_and_body(self):
        conversation = Conversation.objects.create(title="Sizing question", created_by=self.buyer)
        ConversationParticipant.objects.create(conversation=conversation, user=self.buyer)
        ConversationParticipant.objects.create(conversation=conversation, user=self.vendor)

        message = send_message(conversation, self.buyer, "Can you confirm availability?")

        self.assertEqual(message.author, self.buyer)
        self.assertEqual(message.body, "Can you confirm availability?")
        self.assertEqual(conversation.messages.count(), 1)

    def test_notification_mark_read_sets_read_timestamp(self):
        notification = Notification.objects.create(
            user=self.buyer,
            level=Notification.Level.INFO,
            title="New message",
            body="You have a new message.",
        )

        mark_notification_read(notification, self.buyer)

        self.assertIsNotNone(notification.read_at)
        self.assertTrue(notification.is_read)

    def test_toggle_reaction_creates_then_removes(self):
        conversation = Conversation.objects.create(title="Reactions", created_by=self.buyer)
        ConversationParticipant.objects.create(conversation=conversation, user=self.buyer)
        message = send_message(conversation, self.buyer, "Hello!")

        reaction = toggle_reaction(message, self.buyer, "👍")
        self.assertIsNotNone(reaction)
        self.assertEqual(MessageReaction.objects.count(), 1)

        removed = toggle_reaction(message, self.buyer, "👍")
        self.assertIsNone(removed)
        self.assertEqual(MessageReaction.objects.count(), 0)

    def test_thread_close_marks_closed(self):
        conversation = Conversation.objects.create(title="Thread", created_by=self.buyer)
        ConversationParticipant.objects.create(conversation=conversation, user=self.buyer)
        message = send_message(conversation, self.buyer, "Starter")
        thread = conversation.threads.create(title="Follow-up", starter_message=message)

        close_thread(thread, user=self.buyer)

        self.assertEqual(thread.status, thread.Status.CLOSED)
        self.assertIsNotNone(thread.closed_at)

    def test_resolve_dispute_requires_resolution(self):
        dispute = Dispute.objects.create(
            opened_by=self.buyer,
            subject="Missing shipment",
            order_id=42,
        )
        resolved = resolve_dispute(dispute, "Refund issued", actor=self.vendor)
        self.assertEqual(resolved.status, Dispute.Status.RESOLVED)


@override_settings(ROOT_URLCONF="apps.communications.urls")
class CommunicationsApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.buyer = User.objects.create_user(username="buyer", password="pass")
        self.vendor = User.objects.create_user(username="vendor", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(self.buyer)
        self.conversation = Conversation.objects.create(title="Shipping update", created_by=self.buyer)
        ConversationParticipant.objects.create(conversation=self.conversation, user=self.buyer)
        ConversationParticipant.objects.create(conversation=self.conversation, user=self.vendor)

    def test_participant_can_create_message_for_conversation(self):
        url = reverse("conversation-messages", args=(self.conversation.pk,))

        response = self.client.post(url, {"body": "Any tracking update?"}, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().author, self.buyer)

    def test_search_query_records_search_event(self):
        SearchIndex.objects.create(
            entity_type="product",
            entity_id="sku-1",
            title="Organic cotton scarf",
            body="organic cotton scarf",
        )
        url = reverse("search-index-list")

        response = self.client.get(url, {"q": "cotton", "entity_type": "product"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SearchEvent.objects.filter(query="cotton").count(), 1)
