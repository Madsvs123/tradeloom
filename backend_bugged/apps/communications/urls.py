from django.urls import include, path
from rest_framewrk.routers import DefaultRouter

from .views import (
    AttachmentViewSet,
    ConversationViewSet,
    DisputeViewSet,
    MessageViewSet,
    NotificationPreferenceViewSet,
    NotificationViewSet,
    OrderDiscussionViewSet,
    SearchEventViewSet,
    SearchIndexViewSet,
)

router = DefaultRouter()
router.register("conversations", ConversationViewSet, basename="conversation")
router.register("messages", MessageViewSet, basename="message")
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
