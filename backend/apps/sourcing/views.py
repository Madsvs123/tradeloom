from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import (
    AuctionBid,
    BidEvaluation,
    BidLineItem,
    BidPackage,
    EvaluationCriterion,
    ReverseAuction,
    SourcingProject,
    SupplierInvitation,
    Tender,
    TenderDocument,
    TenderLot,
    TenderResponse,
)
from .serializers import (
    AuctionBidSerializer,
    BidEvaluationSerializer,
    BidLineItemSerializer,
    BidPackageSerializer,
    EvaluationCriterionSerializer,
    ReverseAuctionSerializer,
    SourcingProjectSerializer,
    SupplierInvitationSerializer,
    TenderDocumentSerializer,
    TenderLotSerializer,
    TenderResponseSerializer,
    TenderSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)


class SourcingProjectViewSet(AuthenticatedViewSet):
    serializer_class = SourcingProjectSerializer

    def get_queryset(self):
        qs = SourcingProject.objects.prefetch_related("tenders")
        if self.request.user.is_staff:
            return qs
        return qs.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TenderViewSet(AuthenticatedViewSet):
    serializer_class = TenderSerializer

    def get_queryset(self):
        qs = Tender.objects.prefetch_related("lots", "documents", "criteria", "responses")
        if self.request.user.is_staff:
            return qs
        return qs.filter(buyer=self.request.user) | qs.filter(
            responses__supplier=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        tender = wrap_service(services.publish_tender, self.get_object(), actor=request.user)
        return Response(self.get_serializer(tender).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        tender = wrap_service(services.close_tender, self.get_object(), actor=request.user)
        return Response(self.get_serializer(tender).data)

    @action(detail=True, methods=["post"])
    def award(self, request, pk=None):
        tender = self.get_object()
        response = TenderResponse.objects.filter(pk=request.data.get("response")).first()
        if response is None:
            raise ValidationError("A valid response id is required.")
        response = wrap_service(
            services.award_tender,
            tender,
            response,
            actor=request.user,
            notes=request.data.get("notes", ""),
        )
        return Response(self.get_serializer(tender).data)

    @action(detail=True, methods=["post"], url_path="invite-supplier")
    def invite_supplier(self, request, pk=None):
        from django.contrib.auth import get_user_model

        supplier = get_user_model().objects.filter(pk=request.data.get("supplier")).first()
        if supplier is None:
            raise ValidationError("A valid supplier user id is required.")
        invitation = wrap_service(
            services.invite_supplier,
            self.get_object(),
            supplier,
            request.user,
            message=request.data.get("message", ""),
        )
        return Response(SupplierInvitationSerializer(invitation).data, status=status.HTTP_201_CREATED)


class TenderLotViewSet(AuthenticatedViewSet):
    serializer_class = TenderLotSerializer

    def get_queryset(self):
        qs = TenderLot.objects.select_related("tender")
        if self.request.user.is_staff:
            return qs
        return qs.filter(tender__buyer=self.request.user) | qs.filter(
            tender__bid_packages__supplier=self.request.user
        )


class TenderDocumentViewSet(AuthenticatedViewSet):
    serializer_class = TenderDocumentSerializer

    def get_queryset(self):
        qs = TenderDocument.objects.select_related("tender", "uploaded_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(tender__buyer=self.request.user) | qs.filter(
            tender__bid_packages__supplier=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class BidPackageViewSet(AuthenticatedViewSet):
    serializer_class = BidPackageSerializer

    def get_queryset(self):
        qs = BidPackage.objects.select_related("tender", "supplier")
        if self.request.user.is_staff:
            return qs
        return qs.filter(supplier=self.request.user) | qs.filter(tender__buyer=self.request.user)


class TenderResponseViewSet(AuthenticatedViewSet):
    serializer_class = TenderResponseSerializer

    def get_queryset(self):
        qs = TenderResponse.objects.select_related("tender", "supplier").prefetch_related("lines", "evaluations")
        if self.request.user.is_staff:
            return qs
        return qs.filter(supplier=self.request.user) | qs.filter(tender__buyer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(supplier=self.request.user)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        response = wrap_service(services.submit_bid, self.get_object(), actor=request.user)
        return Response(self.get_serializer(response).data)

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        response = wrap_service(services.withdraw_bid, self.get_object(), actor=request.user)
        return Response(self.get_serializer(response).data)

    @action(detail=True, methods=["post"])
    def evaluate(self, request, pk=None):
        scores = request.data.get("scores")
        if not isinstance(scores, dict):
            raise ValidationError("A 'scores' mapping of criterion ids to scores is required.")
        response = wrap_service(
            services.evaluate_bid,
            self.get_object(),
            request.user,
            scores,
            comments=request.data.get("comments", ""),
        )
        return Response(self.get_serializer(response).data)


class BidLineItemViewSet(AuthenticatedViewSet):
    serializer_class = BidLineItemSerializer

    def get_queryset(self):
        qs = BidLineItem.objects.select_related("response", "lot")
        if self.request.user.is_staff:
            return qs
        return qs.filter(response__supplier=self.request.user) | qs.filter(
            response__tender__buyer=self.request.user
        )


class EvaluationCriterionViewSet(AuthenticatedViewSet):
    serializer_class = EvaluationCriterionSerializer

    def get_queryset(self):
        qs = EvaluationCriterion.objects.select_related("tender")
        if self.request.user.is_staff:
            return qs
        return qs.filter(tender__buyer=self.request.user)


class BidEvaluationViewSet(AuthenticatedViewSet):
    serializer_class = BidEvaluationSerializer

    def get_queryset(self):
        qs = BidEvaluation.objects.select_related("response", "criterion", "evaluator")
        if self.request.user.is_staff:
            return qs
        return qs.filter(evaluator=self.request.user) | qs.filter(
            response__tender__buyer=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(evaluator=self.request.user)


class ReverseAuctionViewSet(AuthenticatedViewSet):
    serializer_class = ReverseAuctionSerializer

    def get_queryset(self):
        qs = ReverseAuction.objects.select_related("buyer", "tender").prefetch_related("bids")
        if self.request.user.is_staff:
            return qs
        return qs.filter(buyer=self.request.user) | qs.filter(
            bids__bidder=self.request.user
        ) | qs.filter(tender__bid_packages__supplier=self.request.user)

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        auction = wrap_service(services.start_auction, self.get_object(), actor=request.user)
        return Response(self.get_serializer(auction).data)

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        auction = wrap_service(services.pause_auction, self.get_object(), actor=request.user)
        return Response(self.get_serializer(auction).data)

    @action(detail=True, methods=["post"])
    def resume(self, request, pk=None):
        auction = wrap_service(services.resume_auction, self.get_object(), actor=request.user)
        return Response(self.get_serializer(auction).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        auction = wrap_service(services.close_auction, self.get_object(), actor=request.user)
        return Response(self.get_serializer(auction).data)

    @action(detail=True, methods=["post"], url_path="place-bid")
    def place_bid(self, request, pk=None):
        bid = wrap_service(
            services.place_auction_bid,
            self.get_object(),
            request.user,
            request.data.get("amount"),
        )
        return Response(AuctionBidSerializer(bid).data, status=status.HTTP_201_CREATED)


class AuctionBidViewSet(AuthenticatedViewSet):
    serializer_class = AuctionBidSerializer

    def get_queryset(self):
        qs = AuctionBid.objects.select_related("auction", "bidder")
        if self.request.user.is_staff:
            return qs
        return qs.filter(bidder=self.request.user) | qs.filter(auction__buyer=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auction = serializer.validated_data.get("auction")
        bid = wrap_service(
            services.place_auction_bid,
            auction,
            request.user,
            serializer.validated_data.get("amount"),
        )
        return Response(self.get_serializer(bid).data, status=status.HTTP_201_CREATED)


class SupplierInvitationViewSet(AuthenticatedViewSet):
    serializer_class = SupplierInvitationSerializer

    def get_queryset(self):
        qs = SupplierInvitation.objects.select_related("tender", "supplier", "invited_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(supplier=self.request.user) | qs.filter(tender__buyer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(invited_by=self.request.user)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        invitation = wrap_service(
            services.respond_to_invitation,
            self.get_object(),
            True,
            actor=request.user,
            message=request.data.get("message", ""),
        )
        return Response(self.get_serializer(invitation).data)

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        invitation = wrap_service(
            services.respond_to_invitation,
            self.get_object(),
            False,
            actor=request.user,
            message=request.data.get("message", ""),
        )
        return Response(self.get_serializer(invitation).data)

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        invitation = wrap_service(services.withdraw_invitation, self.get_object(), actor=request.user)
        return Response(self.get_serializer(invitation).data)
