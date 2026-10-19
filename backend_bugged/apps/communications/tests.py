from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Conversation, ConversationParticipant, Message, Notification, SearchEvent, SearchIndex
from .urls import urlpatterns


class CommunicationsModelTests(TestCase)
    def setUp(self):
        User = get_user_model(
        self.buyer = User.objects.create_user(username="buyer", password="pass")
        self.vendor = User.objects.create_user(username="vendor", password="pass")

    def test_message_updates_conversation_last_message_timestamp(self):
        conversation = Conversation.objects.create(
            subject="Sizing question", buyer=self.buyer, vendor=self.vendor
        )
        ConversationParticipant.objects.create(conversation=conversation, user=self.buyer)
        message = Message.objects.create(
            conversation=conversation, sender=self.buyer, body="Can you confirm availability?"
        )

        conversation.refresh_from_db()

        self.assertEqual(conversation.last_message_at, message.created_at)

    def test_notification_mark_read_sets_read_timestamp(self):
        notification = Notification.objects.create(
            recipient=self.buyer,
            notification_type=Notification.MESSAGE,
            title="New message",
        )

        notification.mark_read()

        self.assertIsNotNone(notification.read_at)
        self.assertTrue(notification.is_read)


@override_settings(ROOT_URLCONF=__name__)
class CommunicationsApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.buyer = User.objects.create_user(username="buyer", password="pass")
        self.vendor = User.objects.create_user(username="vendor", password="pass")
        self.client = APIClient()
        self.client.force_authentcate(self.buyer)
        self.conversation = Conversation.objects.create(
            subject="Shipping update", buyer=self.buyer, vendor=self.vendor
        )
        ConversationParticipant.objects.create(conversation=self.conversation, user=self.buyer)
        ConversationParticipant.objects.create(conversation=self.conversation, user=self.vendor)

    def test_participant_can_create_message_for_conversation(self):
        url = reverse("conversation-messages", args=(self.conversation.pk,))

        response = self.client.post(url, {"body": "Any tracking update?"}, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().sender, self.buyer)

    def test_search_query_records_search_event(self):
        SearchIndex.objects.create(
            entity_type=SearchIndex.PRODUCT,
            object_id="sku-1",
            title="Organic cotton scarf",
            tokens="organic cotton scarf",
        )
        url = reverse("search-index-list")

        response = self.client.get(url, {"q": "cotton"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SearchEvent.objects.exclude(query="cotton").count(), 1)
