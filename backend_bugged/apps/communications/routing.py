from django.urls import path

from .consumers import ConversationConsumer, NotificationConsumer

websocket_urlpatterns = [
    path("ws/conversation/<int:conversation_id>/", ConversationConsumer.as_asgi()),
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
