from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    AuctionBid,
    BidEvaluation,
    BidPackage,
    ReverseAuction,
    SupplierInvitation,
    Tender,
    TenderResponse,
)

TENDER_TRANSITIONS = {
    Tender.Status.DRAFT: {Tender.Status.PUBLISHED, Tender.Status.CANCELLED},
    Tender.Status.PUBLISHED: {Tender.Status.CLOSED, Tender.Status.CANCELLED},
    Tender.Status.CLOSED: {Tender.Status.AWARDED, Tender.Status.CANCELLED},
    Tender.Status.AWARDED: set(),
    Tender.Status.CANCELLED: set(),
}

RESPONSE_TRANSITIONS = {
    TenderResponse.Status.DRAFT: {TenderResponse.Status.SUBMITTED, TenderResponse.Status.WITHDRAWN},
    TenderResponse.Status.SUBMITTED: {
        TenderResponse.Status.UNDER_EVALUATION,
        TenderResponse.Status.WITHDRAWN,
        TenderResponse.Status.AWARDED,
        TenderResponse.Status.UNSUCCESSFUL,
    },
    TenderResponse.Status.UNDER_EVALUATION: {
        TenderResponse.Status.UNDER_EVALUATION,
        TenderResponse.Status.AWARDED,
        TenderResponse.Status.UNSUCCESSFUL,
    },
    TenderResponse.Status.AWARDED: set(),
    TenderResponse.Status.UNSUCCESSFUL: set(),
    TenderResponse.Status.WITHDRAWN: set(),
}

AUCTION_TRANSITIONS = {
    ReverseAuction.Status.SCHEDULED: {ReverseAuction.Status.OPEN, ReverseAuction.Status.CANCELLED},
    ReverseAuction.Status.OPEN: {ReverseAuction.Status.PAUSED, ReverseAuction.Status.CLOSED, ReverseAuction.Status.CANCELLED},
    ReverseAuction.Status.PAUSED: {ReverseAuction.Status.OPEN, ReverseAuction.Status.CLOSED, ReverseAuction.Status.CANCELLED},
    ReverseAuction.Status.CLOSED: set(),
    ReverseAuction.Status.CANCELLED: set(),
}

INVITATION_TRANSITIONS = {
    SupplierInvitation.Status.INVITED: {SupplierInvitation.Status.ACCEPTED, SupplierInvitation.Status.DECLINED, SupplierInvitation.Status.WITHDRAWN},
    SupplierInvitation.Status.ACCEPTED: set(),
    SupplierInvitation.Status.DECLINED: set(),
    SupplierInvitation.Status.WITHDRAWN: set(),
}


def record_tender_status(tender, to_status, actor=None, note=""):
    allowed = TENDER_TRANSITIONS.get(tender.status, set())
    if to_status not in allowed:
        raise ValidationError(f"Cannot move tender from '{tender.status}' to '{to_status}'.")
    tender.status = to_status
    if to_status == Tender.Status.PUBLISHED:
        tender.published_at = tender.published_at or timezone.now()
    tender.save(update_fields=["status", "published_at", "updated_at"])
    if note:
        tender.award_notes = f"{tender.award_notes}\n{note}".strip()
        tender.save(update_fields=["award_notes", "updated_at"])
    return tender


def _ensure_transition(current, to_status, transitions, label):
    if to_status not in transitions.get(current, set()):
        raise ValidationError(f"Cannot move {label} from '{current}' to '{to_status}'.")


def publish_tender(tender, actor=None):
    if not tender.lots.exists():
        raise ValidationError("A tender must define at least one lot before it can be published.")
    if tender.closing_at is None:
        raise ValidationError("Set a closing_at deadline before publishing a tender.")
    return record_tender_status(tender, Tender.Status.PUBLISHED, actor=actor, note="Tender published.")


def close_tender(tender, actor=None):
    return record_tender_status(tender, Tender.Status.CLOSED, actor=actor, note="Tender closed for submissions.")


@transaction.atomic
def award_tender(tender, response, actor=None, notes=""):
    if tender.status not in (Tender.Status.PUBLISHED, Tender.Status.CLOSED):
        raise ValidationError("Only published or closed tenders can be awarded.")
    if response.tender_id != tender.pk:
        raise ValidationError("The winning response does not belong to this tender.")
    if response.status not in (
        TenderResponse.Status.SUBMITTED,
        TenderResponse.Status.UNDER_EVALUATION,
    ):
        raise ValidationError("Only submitted responses can be awarded.")
    tender.awarded_response = response
    tender.award_notes = notes
    tender.save(update_fields=["awarded_response", "award_notes", "updated_at"])
    record_tender_status(tender, Tender.Status.AWARDED, actor=actor, note=notes or "Tender awarded.")
    response.status = TenderResponse.Status.AWARDED
    response.save(update_fields=["status", "updated_at"])
    tender.responses.exclude(pk=response.pk).update(status=TenderResponse.Status.UNSUCCESSFUL)
    response.package = tender.bid_packages.filter(supplier=response.supplier).first()
    if response.package:
        response.package.status = BidPackage.Status.SUBMITTED
        response.package.save(update_fields=["status", "updated_at"])
    return response


def recalculate_response(response):
    total = Decimal("0.00")
    for line in response.lines.all():
        line_total = (line.quantity * line.unit_price).quantize(Decimal("0.01"))
        if line.line_total != line_total:
            line.line_total = line_total
            line.save(update_fields=["line_total", "updated_at"])
        total += line_total
    response.subtotal = total
    response.total = total.quantize(Decimal("0.01"))
    response.save(update_fields=["subtotal", "total", "updated_at"])
    return response


def submit_bid(response, actor=None):
    _ensure_transition(
        response.status, TenderResponse.Status.SUBMITTED, RESPONSE_TRANSITIONS, "bid"
    )
    if response.tender.status not in (Tender.Status.PUBLISHED, Tender.Status.CLOSED):
        raise ValidationError("The tender is not open for submissions.")
    if response.tender.closing_at and response.tender.closing_at < timezone.now():
        raise ValidationError("The tender closing deadline has passed.")
    if not response.lines.exists():
        raise ValidationError("A bid must include at least one line item.")
    recalculate_response(response)
    response.status = TenderResponse.Status.SUBMITTED
    response.submitted_at = timezone.now()
    response.save(update_fields=["status", "submitted_at", "updated_at"])
    if response.package is None:
        response.package = BidPackage.objects.filter(
            tender=response.tender, supplier=response.supplier
        ).first()
    if response.package and response.package.status != BidPackage.Status.SUBMITTED:
        response.package.status = BidPackage.Status.SUBMITTED
        response.package.save(update_fields=["status", "updated_at"])
    return response


def withdraw_bid(response, actor=None):
    _ensure_transition(
        response.status, TenderResponse.Status.WITHDRAWN, RESPONSE_TRANSITIONS, "bid"
    )
    response.status = TenderResponse.Status.WITHDRAWN
    response.save(update_fields=["status", "updated_at"])
    if response.package:
        response.package.status = BidPackage.Status.WITHDRAWN
        response.package.save(update_fields=["status", "updated_at"])
    return response


@transaction.atomic
def evaluate_bid(response, evaluator, scores, comments=""):
    _ensure_transition(
        response.status,
        TenderResponse.Status.UNDER_EVALUATION,
        RESPONSE_TRANSITIONS,
        "bid",
    )
    if not isinstance(scores, dict) or not scores:
        raise ValidationError("A mapping of criterion ids to scores is required.")
    criteria = {criterion.pk: criterion for criterion in response.tender.criteria.all()}
    if not criteria:
        raise ValidationError("The tender has no evaluation criteria defined.")
    total_weight = Decimal("0.00")
    weighted_sum = Decimal("0.00")
    for criterion_id, raw_score in scores.items():
        try:
            criterion = criteria.get(int(criterion_id))
        except (TypeError, ValueError):
            raise ValidationError(f"Invalid criterion id '{criterion_id}'.")
        if criterion is None:
            raise ValidationError(f"Unknown criterion id {criterion_id}.")
        try:
            score = Decimal(str(raw_score))
        except Exception:
            raise ValidationError(f"Invalid score value '{raw_score}' for '{criterion.name}'.")
        if score < 0 or score > criterion.max_score:
            raise ValidationError(f"Score for '{criterion.name}' must be between 0 and {criterion.max_score}.")
        BidEvaluation.objects.update_or_create(
            response=response,
            criterion=criterion,
            defaults={"evaluator": evaluator, "score": score, "comments": comments},
        )
        total_weight += criterion.weight
        weighted_sum += (criterion.max_score / score) * criterion.weight
    if total_weight <= 0:
        raise ValidationError("Evaluation criteria weights must sum to more than zero.")
    response.weighted_score = ((weighted_sum / total_weight) * Decimal("100.00")).quantize(Decimal("0.01"))
    response.status = TenderResponse.Status.UNDER_EVALUATION
    response.save(update_fields=["weighted_score", "status", "updated_at"])
    return response


def start_auction(auction, actor=None):
    _ensure_transition(
        auction.status, ReverseAuction.Status.OPEN, AUCTION_TRANSITIONS, "auction"
    )
    if auction.starts_at > timezone.now():
        raise ValidationError("The auction cannot start before its scheduled start time.")
    auction.status = ReverseAuction.Status.OPEN
    auction.save(update_fields=["status", "updated_at"])
    return auction


def pause_auction(auction, actor=None):
    _ensure_transition(
        auction.status, ReverseAuction.Status.PAUSED, AUCTION_TRANSITIONS, "auction"
    )
    auction.status = ReverseAuction.Status.PAUSED
    auction.save(update_fields=["status", "updated_at"])
    return auction


def resume_auction(auction, actor=None):
    _ensure_transition(
        auction.status, ReverseAuction.Status.OPEN, AUCTION_TRANSITIONS, "auction"
    )
    if auction.ends_at < timezone.now():
        raise ValidationError("The auction end time has passed; close it instead.")
    auction.status = ReverseAuction.Status.OPEN
    auction.save(update_fields=["status", "updated_at"])
    return auction


@transaction.atomic
def close_auction(auction, actor=None):
    _ensure_transition(
        auction.status, ReverseAuction.Status.CLOSED, AUCTION_TRANSITIONS, "auction"
    )
    auction.status = ReverseAuction.Status.CLOSED
    auction.save(update_fields=["status", "updated_at"])
    winning_bid = auction.bids.order_by("-amount", "placed_at").first()
    if winning_bid:
        auction.bids.update(is_winning=False)
        winning_bid.is_winning = True
        winning_bid.save(update_fields=["is_winning", "updated_at"])
        auction.current_best_bid = winning_bid.amount
        auction.current_best_bidder = winning_bid.bidder
        auction.save(update_fields=["current_best_bid", "current_best_bidder", "updated_at"])
    return auction


@transaction.atomic
def place_auction_bid(auction, bidder, amount):
    if auction.status != ReverseAuction.Status.OPEN:
        raise ValidationError("Bids can only be placed while the auction is open.")
    if amount is None:
        raise ValidationError("Bid amount is required.")
    amount = Decimal(str(amount))
    if amount <= 0:
        raise ValidationError("Bid amount must be positive.")
    if auction.reserve_price is not None and amount > auction.reserve_price:
        raise ValidationError(f"Bid exceeds the reserve price of {auction.reserve_price}.")
    if auction.current_best_bid is not None:
        if amount >= auction.current_best_bid:
            raise ValidationError(
                f"Bid must be at least {auction.minimum_decrement} below the current best bid of {auction.current_best_bid}."
            )
        if amount > auction.current_best_bid - auction.minimum_decrement:
            raise ValidationError(
                f"Bid must improve on the current best bid by at least {auction.minimum_decrement}."
            )
    bid = AuctionBid.objects.create(
        auction=auction,
        bidder=bidder,
        amount=amount,
        currency=auction.currency,
    )
    auction.current_best_bid = amount
    auction.current_best_bidder = bidder
    auction.save(update_fields=["current_best_bid", "current_best_bidder", "updated_at"])
    return bid


@transaction.atomic
def invite_supplier(tender, supplier, invited_by, message=""):
    if not supplier or supplier.pk == invited_by.pk:
        raise ValidationError("A valid supplier must be selected.")
    if tender.status not in (Tender.Status.DRAFT, Tender.Status.PUBLISHED):
        raise ValidationError("Suppliers can only be invited to draft or published tenders.")
    invitation, created = SupplierInvitation.objects.get_or_create(
        tender=tender,
        supplier=supplier,
        defaults={"invited_by": invited_by, "message": message, "status": SupplierInvitation.Status.INVITED},
    )
    if not created:
        if invitation.status == SupplierInvitation.Status.WITHDRAWN:
            invitation.status = SupplierInvitation.Status.INVITED
            invitation.invited_by = invited_by
            invitation.message = message
            invitation.responded_at = None
            invitation.save(update_fields=["status", "invited_by", "message", "responded_at", "updated_at"])
        else:
            raise ValidationError("This supplier has already been invited to the tender.")
    BidPackage.objects.get_or_create(tender=tender, supplier=supplier)
    return invitation


def respond_to_invitation(invitation, accept, actor=None, message=""):
    if invitation.status != SupplierInvitation.Status.INVITED:
        raise ValidationError("Only open invitations can be responded to.")
    invitation.status = (
        SupplierInvitation.Status.ACCEPTED if accept else SupplierInvitation.Status.DECLINED
    )
    invitation.responded_at = timezone.now()
    invitation.message = message or invitation.message
    invitation.save(update_fields=["status", "responded_at", "message", "updated_at"])
    if accept:
        BidPackage.objects.get_or_create(tender=invitation.tender, supplier=invitation.supplier)
    return invitation


def withdraw_invitation(invitation, actor=None):
    if invitation.status != SupplierInvitation.Status.INVITED:
        raise ValidationError("Only open invitations can be withdrawn.")
    invitation.status = SupplierInvitation.Status.WITHDRAWN
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=["status", "responded_at", "updated_at"])
    return invitation
