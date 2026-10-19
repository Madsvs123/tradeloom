from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import (
    EvaluationCriterion,
    EvaluationScore,
    NegotiationMessage,
    NegotiationRoom,
    QuotationComparisonSnapshot,
    RFQ,
    RFQAttachment,
    RFQDocument,
    RfqTemplate,
    SupplierCounterOffer,
    SupplierQuotation,
)
from .serializers import (
    EvaluationCriterionSerializer,
    EvaluationScoreSerializer,
    NegotiationMessageSerializer,
    NegotiationRoomSerializer,
    QuotationComparisonSnapshotSerializer,
    RFQAttachmentSerializer,
    RFQDocumentSerializer,
    RFQSerializer,
    RFQSupplierSerializer,
    RfqTemplateSerializer,
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

    @action(detail=True, methods=["get"])
    def issue(self, request, pk=None):
        rfq = wrap_service(services.issue_rfq, self.get_object(), actor=request.user)
        return Response(self.get_serializer(rfq).data)

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        rfq = self.get_object()
        invite = rfq.invited_suppliers.filter(supplier=request.user).first()
        if invite is None:
            raise ValidationError("You were not invited to this RFQ.")
        invite = wrap_service(services.decline_rfq, invite, request.data.get("reason", ""), actor=request.user)
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
            file_name=request.data.get("file_name") or getattr(request.FILES.get("file"), "name", ""),
            file_url=request.data.get("file_url", ""),
            rfq=self.get_object(),
            content_type=request.data.get("content_type", ""),
        )
        return Response(RFQAttachmentSerializer(attachment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="upload_document")
    def upload_document(self, request, pk=None):
        document = wrap_service(
            services.upload_rfq_document,
            self.get_object(),
            title=request.data.get("title", ""),
            document_type=request.data.get("document_type", "other"),
            file_name=request.data.get("file_name") or getattr(request.FILES.get("file"), "name", ""),
            file_url=request.data.get("file_url", ""),
            uploaded_by=request.user,
        )
        return Response(RFQDocumentSerializer(document).data, status=status.HTTP_201_CREATED)


class SupplierQuotationViewSet(AuthenticatedViewSet):
    serializer_class = SupplierQuotationSerializer

    def get_queryset(self):
        qs = SupplierQuotation.objects.prefetch_related("lines")
        if self.request.user.is_staff:
            return qs
        return qs.filter(supplier=self.request.user)

    def perform_create(self, serializer):
        serializer.save(supplier=self.request.user)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        quotation = wrap_service(services.submit_quotation, self.get_object(), actor=request.user)
        return Response(self.get_serializer(quotation).data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        quotation = wrap_service(
            services.accept_quotation,
            self.get_object(),
            actor=request.user,
            award_reason=request.data.get("award_reason", ""),
        )
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


class RfqTemplateViewSet(AuthenticatedViewSet):
    serializer_class = RfqTemplateSerializer

    def get_queryset(self):
        qs = RfqTemplate.objects.all()
        if self.request.user.is_staff:
            return qs
        return qs.filter(owner=self.request.user) | qs.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        template = wrap_service(services.activate_template, self.get_object())
        return Response(self.get_serializer(template).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        template = wrap_service(services.archive_template, self.get_object())
        return Response(self.get_serializer(template).data)

    @action(detail=True, methods=["post"])
    def instantiate(self, request, pk=None):
        rfq = wrap_service(
            services.instantiate_template,
            self.get_object(),
            request.user,
            title=request.data.get("title"),
        )
        return Response(RFQSerializer(rfq).data, status=status.HTTP_201_CREATED)


class EvaluationCriterionViewSet(AuthenticatedViewSet):
    serializer_class = EvaluationCriterionSerializer

    def get_queryset(self):
        qs = EvaluationCriterion.objects.select_related("rfq")
        rfq_id = self.request.query_params.get("rfq")
        if rfq_id:
            qs = qs.filter(rfq_id=rfq_id)
        return qs


class EvaluationScoreViewSet(AuthenticatedViewSet):
    serializer_class = EvaluationScoreSerializer

    def get_queryset(self):
        return EvaluationScore.objects.select_related("criterion", "quotation", "scored_by")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = wrap_service(
            services.score_quotation,
            serializer.validated_data["criterion"],
            serializer.validated_data["quotation"],
            serializer.validated_data["score"],
            request.user,
            passed=serializer.validated_data.get("passed", True),
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(self.get_serializer(record).data, status=status.HTTP_201_CREATED)


class QuotationComparisonSnapshotViewSet(AuthenticatedViewSet):
    serializer_class = QuotationComparisonSnapshotSerializer

    def get_queryset(self):
        qs = QuotationComparisonSnapshot.objects.select_related("rfq", "created_by")
        rfq_id = self.request.query_params.get("rfq")
        if rfq_id:
            qs = qs.filter(rfq_id=rfq_id)
        return qs

    @action(detail=False, methods=["post"], url_path="build")
    def build(self, request):
        rfq_id = request.data.get("rfq")
        if not rfq_id:
            raise ValidationError("An rfq id is required.")
        rfq = RFQ.objects.filter(pk=rfq_id).first()
        if rfq is None:
            raise ValidationError("RFQ not found.")
        snapshot = wrap_service(services.build_comparison_snapshot, rfq, actor=request.user)
        return Response(self.get_serializer(snapshot).data, status=status.HTTP_201_CREATED)


class RfqDocumentViewSet(AuthenticatedViewSet):
    serializer_class = RfqDocumentSerializer

    def get_queryset(self):
        qs = RfqDocument.objects.select_related("rfq", "uploaded_by")
        rfq_id = self.request.query_params.get("rfq")
        if rfq_id:
            qs = qs.filter(rfq_id=rfq_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class NegotiationRoomViewSet(AuthenticatedViewSet):
    serializer_class = NegotiationRoomSerializer

    def get_queryset(self):
        qs = NegotiationRoom.objects.select_related("rfq", "opened_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(rfq__buyer=self.request.user) | qs.filter(rfq__invited_suppliers__supplier=self.request.user)

    @action(detail=False, methods=["post"], url_path="open")
    def open_room(self, request):
        rfq_id = request.data.get("rfq")
        if not rfq_id:
            raise ValidationError("An rfq id is required.")
        rfq = RFQ.objects.filter(pk=rfq_id).first()
        if rfq is None:
            raise ValidationError("RFQ not found.")
        room = wrap_service(services.create_negotiation_room, rfq, actor=request.user)
        return Response(self.get_serializer(room).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def add_participant(self, request, pk=None):
        user_id = request.data.get("user_id")
        if not user_id:
            raise ValidationError("A user_id is required.")
        room = wrap_service(self.get_object().add_participant, int(user_id))
        return Response(self.get_serializer(room).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        room = wrap_service(services.close_negotiation_room, self.get_object())
        return Response(self.get_serializer(room).data)
