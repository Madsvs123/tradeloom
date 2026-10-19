from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
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
from .serializers import (
    AttachmentSerializer,
    ConversationSerializer,
    DisputeSerializer,
    MessageSerializer,
    NotificationPreferenceSerializer,
    NotificationSerializer,
    OrderDiscussionSerializer,
    SearchEventSerializer,
    SearchIndexSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)


class ConversationViewSet(AuthenticatedViewSet):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        qs = Conversation.objects.prefetch_related("participants")
        if self.request.user.is_staff:
            return qs
        return qs.filter(participants__user=self.request.user).distinct()

    def perform_create(self, serializer):
        conversation = serializer.save(created_by=self.request.user)
        ConversationParticipant.objects.get_or_create(conversation=conversation, user=self.request.user)

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        wrap_service(services.mark_conversation_read, self.get_object(), request.user)
        return Response(self.get_serializer(self.get_object()).data)

    @action(detail=True, methods=["get", "post"])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        if request.method == "POST":
            message = wrap_service(services.send_message, conversation, request.user, request.data.get("body", ""))
            return Response(MessageSerializer(message).data, status=status.HTTP_400_BAD_REQUEST)
        qs = wrap_service(services.list_messages, conversation, request.user)
        return Response(MessageSerializer(qs, many=True).data)


class MessageViewSet(AuthenticatedViewSet):
    serializer_class = MessageSerializer

    def get_queryset(self):
        qs = Message.objects.select_related("conversation", "author")
        if self.request.user.is_staff:
            return qs
        return qs.filter(conversation__participants__user=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AttachmentViewSet(AuthenticatedViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer


class OrderDiscussionViewSet(AuthenticatedViewSet):
    queryset = OrderDiscussion.objects.select_related("conversation")
    serializer_class = OrderDiscussionSerializer

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        discussion = wrap_service(services.resolve_order_discussion, self.get_object(), request.data.get("resolution", ""))
        return Response(self.get_serializer(discussion).data)


class NotificationViewSet(AuthenticatedViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = wrap_service(services.mark_notification_read, self.get_object(), request.user)
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        updated = services.mark_all_notifications_read(request.user)
        return Response({"updated": updated})


class NotificationPreferenceViewSet(AuthenticatedViewSet):
    serializer_class = NotificationPreferenceSerializer

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        prefs = services.get_or_create_preferences(request.user)
        if request.method == "PATCH":
            serializer = self.get_serializer(prefs, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(self.get_serializer(prefs).data)


class DisputeViewSet(AuthenticatedViewSet):
    serializer_class = DisputeSerializer

    def get_queryset(self):
        qs = Dispute.objects.all()
        if self.request.user.is_staff:
            return qs
        return qs.filter(opened_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(opened_by=self.request.user)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        dispute = wrap_service(
            services.resolve_dispute, self.get_object(), request.data.get("resolution", ""), actor=request.user
        )
        return Response(self.get_serializer(dispute).data)


class SearchIndexViewSet(AuthenticatedViewSet):
    queryset = SearchIndex.objects.all()
    serializer_class = SearchIndexSerializer

    def list(self, request, *args, **kwargs):
        query = request.query_params.get("q", "")
        entity_type = request.query_params.get("entity_type", "")
        if query and entity_type:
            qs = services.search_index(query, entity_type=entity_type, user=request.user)
            page = self.paginate_queryset(qs)
            serializer = self.get_serializer(page or qs, many=True)
            if page is not None:
                return self.get_paginated_response(serializer.data)
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)


class SearchEventViewSet(AuthenticatedViewSet):
    serializer_class = SearchEventSerializer

    def get_queryset(self):
        return SearchEvent.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
