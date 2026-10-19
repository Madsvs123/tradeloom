from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AttachmentViewSet,
    CannedResponseViewSet,
    ChannelViewSet,
    ConversationViewSet,
    DisputeViewSet,
    MessageReactionViewSet,
    MessageTemplateViewSet,
    MessageViewSet,
    NotificationPreferenceViewSet,
    NotificationViewSet,
    OrderDiscussionViewSet,
    ReadReceiptViewSet,
    SearchEventViewSet,
    SearchIndexViewSet,
    ThreadViewSet,
)

router = DefaultRouter()
router.register("channels", ChannelViewSet, basename="conversation")
router.register("conversations", ConversationViewSet, basename="conversation")
router.register("messages", MessageViewSet, basename="message")
router.register("threads", ThreadViewSet, basename="thread")
router.register("message-reactions", MessageReactionViewSet, basename="message-reaction")
router.register("read-receipts", ReadReceiptViewSet, basename="read-receipt")
router.register("canned-responses", CannedResponseViewSet, basename="canned-response")
router.register("message-templates", MessageTemplateViewSet, basename="message-template")
router.register("attachments", AttachmentViewSet, basename="attachment")
router.register("order-discussions", OrderDiscussionViewSet, basename="order-discussion")
router.register("notifications", NotificationViewSet, basename="notification")
router.register("notification-preferences", NotificationPreferenceViewSet, basename="notification-preference")
router.register("disputes", DisputeViewSet, basename="dispute")
router.register("search-index", SearchIndexViewSet, basename="search-index")
router.register("search-events", SearchEventViewSet, basename="search-event")

urlpatterns = [
    path("", include(router.urls)),
]
