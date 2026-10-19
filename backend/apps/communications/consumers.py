from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import ConversationParticipant, Notification
from .serializers import MessageSerializer, NotificationSerializer
from .services import send_message


class ConversationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not getattr(user, "is_authenticated", False):
            await self.close()
            return
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.group_name = f"conversation_{self.conversation_id}"
        allowed = await sync_to_async(self._is_participant)(user)
        if not allowed:
            await self.close()
            return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    def _is_participant(self, user):
        return user.is_staff or ConversationParticipant.objects.filter(
            conversation_id=self.conversation_id, user=user
        ).exists()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        body = content.get("body", "")
        user = self.scope["user"]

        def _create():
            from .models import Conversation

            conversation = Conversation.objects.get(pk=self.conversation_id)
            return send_message(conversation, user, body)

        try:
            message = await sync_to_async(_create)()
        except Exception as exc:
            await self.send_json({"error": str(exc)})
            return
        payload = await sync_to_async(lambda: MessageSerializer(message).data)()
        await self.channel_layer.group_send(self.group_name, {"type": "chat.message", "message": payload})

    async def chat_message(self, event):
        await self.send_json(event["message"])


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not getattr(user, "is_authenticated", False):
            await self.close()
            return
        self.group_name = f"notifications_{user.pk}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        user = self.scope["user"]
        notifications = await sync_to_async(list)(Notification.objects.filter(user=user, read_at__isnull=True)[:20])
        payload = await sync_to_async(lambda: NotificationSerializer(notifications, many=True).data)()
        await self.send_json({"unread": payload})

    async def notify(self, event):
        await self.send_json(event.get("notification", event))
