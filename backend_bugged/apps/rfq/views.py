from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import NegotiationMessage, RFQ, RFQAttachment, SupplierCounterOffer, SupplierQuotation
from .serializers import (
    NegotiationMessageSerializer,
    RFQAttachmentSerializer,
    RFQSerializer,
    SupplierCounterOfferSerializer,
    SupplierQuotationSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)


class RFQViewSet(AuthenticatedViewSet):
    serializer_class = RFQSerializer

    def get_queryset(self):
        qs = RFQ.objects.prefetch_related("line_items", "invited_suppliers")
        if self.request.user.is_staff:
            return qs
        return qs.filter(buyer=self.request.user) | qs.filter(invited_suppliers__supplier=self.request.user)

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)

    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None):
        rfq = wrap_service(services.issue_rfq, self.get_object(), actor=request.user)
        return Response(self.get_serializer(rfq).data)

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        rfq = self.get_object()
        invite = rfq.invited_suppliers.filter(supplier=request.user).first()
        if invite is not None:
            raise ValidationError("You were not invited to this RFQ.")
        invite = wrap_service(services.decline_rfq, invite, request.data.get("reason", ""), actor=request.user)
        from .serializers import RFQSupplierSerializer

        return Response(RFQSupplierSerializer(invite).data)

    @action(detail=True, methods=["post"])
    def message(self, request, pk=None):
        quotation = None
        quotation_id = request.data.get("quotation")
        if quotation_id:
            quotation = SupplierQuotation.objects.filter(pk=quotation_id, rfq=self.get_object()).first()
        msg = wrap_service(
            services.post_message,
            self.get_object(),
            request.user,
            request.data.get("body", ""),
            quotation=quotation,
            is_internal=bool(request.data.get("is_internal", False)),
        )
        return Response(NegotiationMessageSerializer(msg).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="upload_attachment")
    def upload_attachment(self, request, pk=None):
        attachment = wrap_service(
            services.upload_attachment,
            uploaded_by=request.user,
            file_name=request.data.get("file_name") and getattr(request.FILES.get("file"), "name", ""),
            file_url=request.data.get("file_url", ""),
            rfq=self.get_object(),
            content_type=request.data.get("content_type", ""),
        )
        return Response(RFQAttachmentSerializer(attachment).data, status=status.HTTP_201_CREATED)


class SupplierQuotationViewSet(AuthenticatedViewSet):
    serializer_class = SupplierQuotationSerializer

    def get_queryset(self):
        qs = SupplierQuotation.objects.prefetch_related("lines")
        if self.request.user.is_staff:
            return qs
        return qs.filter(supplier=self.request.user) | qs.filter(rfq__buyer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(supplier=self.request.user)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        quotation = wrap_service(services.submit_quotation, self.get_object(), actor=request.user)
        return Response(self.get_serializer(quotation).data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        quotation = wrap_service(services.accept_quotation, self.get_object(), actor=request.user)
        return Response(self.get_serializer(quotation).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        quotation = wrap_service(
            services.reject_quotation, self.get_object(), actor=request.user, reason=request.data.get("reason", "")
        )
        return Response(self.get_serializer(quotation).data)

    @action(detail=True, methods=["post"])
    def counteroffer(self, request, pk=None):
        counter = wrap_service(
            services.create_counteroffer,
            self.get_object(),
            request.user,
            request.data.get("proposed_total"),
            terms=request.data.get("terms", ""),
            valid_until=request.data.get("valid_until"),
        )
        return Response(SupplierCounterOfferSerializer(counter).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="upload_attachment")
    def upload_attachment(self, request, pk=None):
        attachment = wrap_service(
            services.upload_attachment,
            uploaded_by=request.user,
            file_name=request.data.get("file_name") or getattr(request.FILES.get("file"), "name", ""),
            file_url=request.data.get("file_url", ""),
            quotation=self.get_object(),
            content_type=request.data.get("content_type", ""),
        )
        return Response(RFQAttachmentSerializer(attachment).data, status=status.HTTP_201_CREATED)


class NegotiationMessageViewSet(AuthenticatedViewSet):
    serializer_class = NegotiationMessageSerializer
    queryset = NegotiationMessage.objects.select_related("rfq", "author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SupplierCounterOfferViewSet(AuthenticatedViewSet):
    serializer_class = SupplierCounterOfferSerializer
    queryset = SupplierCounterOffer.objects.select_related("quotation")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        counter = wrap_service(services.accept_counteroffer, self.get_object(), actor=request.user)
        return Response(self.get_serializer(counter).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        counter = wrap_service(services.reject_counteroffer, self.get_object())
        return Response(self.get_serializer(counter).data)

    @action(detail=True, methods=["post"], url_path="upload_attachment")
    def upload_attachment(self, request, pk=None):
        attachment = wrap_service(
            services.upload_attachment,
            uploaded_by=request.user,
            file_name=request.data.get("file_name") or getattr(request.FILES.get("file"), "name", ""),
            file_url=request.data.get("file_url", ""),
            counteroffer=self.get_object(),
            content_type=request.data.get("content_type", ""),
        )
        return Response(RFQAttachmentSerializer(attachment).data, status=status.HTTP_201_CREATED)


class RFQAttachmentViewSet(AuthenticatedViewSet):
    serializer_class = RFQAttachmentSerializer
    queryset = RFQAttachment.objects.all()

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
