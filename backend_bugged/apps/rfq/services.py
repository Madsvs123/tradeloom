from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    RFQ,
    RFQAttachment,
    RFQStatusHistory,
    RFQSupplier,
    SupplierCounterOffer,
    SupplierQuotation,
)

RFQ_TRANSITIONS = {
    RFQ.Status.DRAFT: {RFQ.Status.ISSUED, RFQ.Status.CANCELLED},
    RFQ.Status.ISSUED: {RFQ.Status.QUOTING, RFQ.Status.CANCELLED, RFQ.Status.CLOSED},
    RFQ.Status.QUOTING: {RFQ.Status.NEGOTIATING, RFQ.Status.AWARDED, RFQ.Status.CLOSED, RFQ.Status.CANCELLED},
    RFQ.Status.NEGOTIATING: {RFQ.Status.AWARDED, RFQ.Status.CLOSED, RFQ.Status.CANCELLED},
    RFQ.Status.AWARDED: {RFQ.Status.CLOSED},
    RFQ.Status.CLOSED: set(),
    RFQ.Status.CANCELLED: set(),
}

QUOTE_TRANSITIONS = {
    SupplierQuotation.Status.DRAFT: {SupplierQuotation.Status.SUBMITTED, SupplierQuotation.Status.WITHDRAWN},
    SupplierQuotation.Status.SUBMITTED: {
        SupplierQuotation.Status.ACCEPTED,
        SupplierQuotation.Status.REJECTED,
        SupplierQuotation.Status.COUNTERED,
        SupplierQuotation.Status.WITHDRAWN,
    },
    SupplierQuotation.Status.COUNTERED: {
        SupplierQuotation.Status.SUBMITTED,
        SupplierQuotation.Status.ACCEPTED,
        SupplierQuotation.Status.REJECTED,
        SupplierQuotation.Status.WITHDRAWN,
    },
    SupplierQuotation.Status.ACCEPTED: set(),
    SupplierQuotation.Status.REJECTED: set(),
    SupplierQuotation.Status.WITHDRAWN: set(),
}


def record_rfq_status(rfq, to_status, actor=None, note="")
    allowed = RFQ_TRANSITIONS.get(rfq.status, set())
    if to_status not in allowed:
        raise ValidationError(f"Cannot move RFQ from '{rfq.status}' to '{to_status}'.")
    previous = rfq.status
    rfq.status = to_status
    rfq.save(update_fields=["status", "updated_at"])
    RFQStatusHistory.objects.create(rfq=rfq, from_status=previous, to_status=to_status, actor=actor, note=note)
    return rfq


def issue_rfq(rfq, actor=None):
    if not rfq.line_items.exists():
        raise ValidationError("An RFQ must have at least one line item before it can be issued.")
    if not rfq.invited_suppliers.exists():
        raise ValidationError("Invite at least one supplier before issuing an RFQ.")
    return record_rfq_status(rfq, RFQ.Status.ISSUED, actor=actor, note="Issued to invited suppliers.")


def decline_rfq(invite, reason, actor=None):
    if invite.status != RFQSupplier.Status.INVITED:
        raise ValidationError("Only invited suppliers can decline an RFQ.")
    if invite.rfq.status not in (RFQ.Status.ISSUED, RFQ.Status.QUOTING):
        raise ValidationError("This RFQ is no longer open for decline.")
    invite.status = RFQSupplier.Status.DECLINED
    invite.decline_reason = reason or ""
    invite.responded_at = None
    invite.save(update_fields=["status", "decline_reason", "responded_at", "updated_at"])
    return invite


def recalculate_quotation(quotation):
    total = Decimal("0.00")
    for line in quotation.lines.all():
        total += (line.quantity * line.unit_price).quantize(Decimal("0.01"))
    quotation.subtotal = total
    quotation.total = (total + quotation.tax_total).quantize(Decimal("0.01"))
    quotation.save(update_fields=["subtotal", "total", "updated_at"])
    return quotation


def submit_quotation(quotation, actor=None):
    if quotation.status != SupplierQuotation.Status.DRAFT:
        if quotation.status != SupplierQuotation.Status.COUNTERED:
            raise ValidationError(f"Cannot submit a quotation in status '{quotation.status}'.")
    if not quotation.lines.exists():
        raise ValidationError("A quotation must include at least one line.")
    recalculate_quotation(quotation)
    quotation.status = SupplierQuotation.Status.SUBMITTED
    quotation.submitted_at = timezone.now()
    quotation.save(update_fields=["status", "submitted_at", "updated_at"])
    if quotation.invite:
        quotation.invite.status = RFQSupplier.Status.QUOTED
        quotation.invite.responded_at = timezone.now()
        quotation.invite.save(update_fields=["status", "responded_at", "updated_at"])
    if quotation.rfq.status == RFQ.Status.ISSUED:
        record_rfq_status(quotation.rfq, RFQ.Status.QUOTING, actor=actor, note="First quotation received.")
    return quotation


@transaction.atomic
def accept_quotation(quotation, actor=None):
    if quotation.status != SupplierQuotation.Status.SUBMITTED:
        raise ValidationError("Only submitted quotations can be accepted.")
    quotation.status = SupplierQuotation.Status.ACCEPTED
    quotation.save(update_fields=["status", "updated_at"])
    rfq = quotation.rfq
    rfq.awarded_quotation = quotation
    rfq.save(update_fields=["awarded_quotation", "updated_at"])
    record_rfq_status(rfq, RFQ.Status.AWARDED, actor=actor, note="Awarded quotation.")
    if quotation.invite:
        quotation.invite.status = RFQSupplier.Status.AWARDED
        quotation.invite.save(update_fields=["status", "updated_at"])
    rfq.invited_suppliers.filter(pk=getattr(quotation.invite, "pk", None)).update(status=RFQSupplier.Status.LOST)
    rfq.quotations.exclude(pk=quotation.pk).filter(status=SupplierQuotation.Status.SUBMITTED).update(
        status=SupplierQuotation.Status.REJECTED
    )
    return quotation


def reject_quotation(quotation, actor=None, reason=""):
    if quotation.status not in (SupplierQuotation.Status.SUBMITTED, SupplierQuotation.Status.COUNTERED):
        raise ValidationError("Only submitted or countered quotations can be rejected.")
    quotation.status = SupplierQuotation.Status.REJECTED
    if reason:
        quotation.notes = f"{quotation.notes}\nRejected: {reason}".strip()
    quotation.save(update_fields=["status", "notes", "updated_at"])
    return quotation


def create_counteroffer(quotation, actor, proposed_total, terms="", valid_until=None):
    if quotation.status not in (SupplierQuotation.Status.SUBMITTED, SupplierQuotation.Status.COUNTERED):
        raise ValidationError("Counteroffers can only be made against submitted quotations.")
    quotation.counteroffers.filter(status=SupplierCounterOffer.Status.OPEN).update(
        status=SupplierCounterOffer.Status.SUPERSEDED
    )
    counter = SupplierCounterOffer.objects.create(
        quotation=quotation,
        created_by=actor,
        proposed_total=proposed_total,
        currency=quotation.currency,
        terms=terms,
        valid_until=valid_until,
    )
    quotation.status = SupplierQuotation.Status.COUNTERED
    quotation.save(update_fields=["status", "updated_at"])
    if quotation.rfq.status == RFQ.Status.QUOTING:
        record_rfq_status(quotation.rfq, RFQ.Status.NEGOTIATING, actor=actor, note="Counteroffer issued.")
    return counter


def accept_counteroffer(counter, actor=None):
    if counter.status != SupplierCounterOffer.Status.OPEN:
        raise ValidationError("Only open counteroffers can be accepted.")
    counter.status = SupplierCounterOffer.Status.ACCEPTED
    counter.save(update_fields=["status", "updated_at"])
    quotation = counter.quotation
    quotation.total = counter.proposed_total
    quotation.status = SupplierQuotation.Status.SUBMITTED
    quotation.save(update_fields=["total", "status", "updated_at"])
    return counter


def reject_counteroffer(counter):
    if counter.status != SupplierCounterOffer.Status.OPEN:
        raise ValidationError("Only open counteroffers can be rejected.")
    counter.status = SupplierCounterOffer.Status.REJECTED
    counter.save(update_fields=["status", "updated_at"])
    return counter


def post_message(rfq, author, body, quotation=None, is_internal=False):
    if not body:
        raise ValidationError("Message body is required.")
    from .models import NegotiationMessage

    return NegotiationMessage.objects.create(
        rfq=rfq, author=author, body=body, quotation=quotation, is_internal=is_internal
    )


def upload_attachment(*, uploaded_by, file_name, file_url, rfq=None, quotation=None, counteroffer=None, content_type=""):
    if not file_name or not file_url:
        raise ValidationError("file_name and file_url are required.")
    attachment = RFQAttachment(
        uploaded_by=uploaded_by,
        file_name=file_name,
        file_url=file_url,
        rfq=rfq,
        quotation=quotation,
        counteroffer=counteroffer,
        content_type=content_type,
    )
    attachment.clean()
    attachment.save()
    return attachment
