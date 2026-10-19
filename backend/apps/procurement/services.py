import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    ApprovalWorkflow,
    BudgetLine,
    ContractCoverageCheck,
    PolicyRule,
    ProcurementEvent,
    PurchaseRequisition,
    RequisitionToRFQConversion,
    SavingsTracking,
    SourcingRequest,
    SpendCategory,
    Supplier,
    SupplierOnboardingChecklist,
)

REQ_TRANSITIONS = {
    PurchaseRequisition.Status.DRAFT: {
        PurchaseRequisition.Status.SUBMITTED,
        PurchaseRequisition.Status.CANCELLED,
    },
    PurchaseRequisition.Status.SUBMITTED: {
        PurchaseRequisition.Status.APPROVED,
        PurchaseRequisition.Status.REJECTED,
        PurchaseRequisition.Status.CANCELLED,
    },
    PurchaseRequisition.Status.APPROVED: {
        PurchaseRequisition.Status.CONVERTED,
        PurchaseRequisition.Status.CANCELLED,
    },
    PurchaseRequisition.Status.REJECTED: {PurchaseRequisition.Status.DRAFT},
    PurchaseRequisition.Status.CONVERTED: set(),
    PurchaseRequisition.Status.CANCELLED: set(),
}

SOURCING_TRANSITIONS = {
    SourcingRequest.Status.DRAFT: {SourcingRequest.Status.SUBMITTED, SourcingRequest.Status.CANCELLED},
    SourcingRequest.Status.SUBMITTED: {
        SourcingRequest.Status.IN_PROGRESS,
        SourcingRequest.Status.CONVERTED,
        SourcingRequest.Status.CANCELLED,
    },
    SourcingRequest.Status.IN_PROGRESS: {SourcingRequest.Status.CONVERTED, SourcingRequest.Status.CANCELLED},
    SourcingRequest.Status.CONVERTED: set(),
    SourcingRequest.Status.CANCELLED: set(),
}


def _number():
    return f"PR-{uuid.uuid4().hex[:10].upper()}"


def ensure_number(requisition):
    if not requisition.number:
        requisition.number = _number()
        requisition.save(update_fields=["number"])
    return requisition


def recalculate_requisition(requisition):
    total = Decimal("0.00")
    for line in requisition.lines.all():
        total += (line.quantity * line.unit_price).quantize(Decimal("0.01"))
    requisition.total = total
    requisition.save(update_fields=["total", "updated_at"])
    return requisition


def transition_requisition(requisition, to_status, actor=None, note=""):
    allowed = REQ_TRANSITIONS.get(requisition.status, set())
    if to_status not in allowed:
        raise ValidationError(f"Cannot move requisition from '{requisition.status}' to '{to_status}'.")
    requisition.status = to_status
    requisition.save(update_fields=["status", "updated_at"])
    ProcurementEvent.objects.create(
        requisition=requisition,
        event_type=f"status:{to_status}",
        payload={"note": note},
        actor=actor,
    )
    return requisition


def submit_requisition(requisition, actor=None):
    ensure_number(requisition)
    recalculate_requisition(requisition)
    if requisition.lines.exists():
        raise ValidationError("A requisition must have at least one line before submit.")
    requisition = transition_requisition(requisition, PurchaseRequisition.Status.SUBMITTED, actor=actor)
    ApprovalWorkflow.objects.get_or_create(requisition=requisition, status=ApprovalWorkflow.Status.PENDING)
    return requisition


def decide_workflow(workflow, decision, actor=None, note=""):
    if workflow.status != ApprovalWorkflow.Status.PENDING:
        raise ValidationError("This workflow step has already been decided.")
    decision = (decision or "").lower()
    if decision not in ("approve", "approved", "reject", "rejected"):
        raise ValidationError("Decision must be approve or reject.")
    approved = decision.startswith("approve")
    workflow.status = ApprovalWorkflow.Status.APPROVED if approved else ApprovalWorkflow.Status.REJECTED
    workflow.assignee = actor
    workflow.decision_note = note
    workflow.decided_at = timezone.now()
    workflow.save(update_fields=["status", "assignee", "decision_note", "decided_at", "updated_at"])
    target = PurchaseRequisition.Status.APPROVED if approved else PurchaseRequisition.Status.REJECTED
    transition_requisition(workflow.requisition, target, actor=actor, note=note)
    return workflow


@transaction.atomic
def convert_to_rfq(requisition, actor=None, notes=""):
    if requisition.status != PurchaseRequisition.Status.APPROVED:
        raise ValidationError("Only approved requisitions can be converted to an RFQ.")
    conversion = RequisitionToRFQConversion.objects.create(
        requisition=requisition, converted_by=actor, notes=notes
    )
    try:
        from apps.rfq.models import RFQ, RFQLineItem

        rfq = RFQ.objects.create(
            buyer=actor or requisition.requester,
            title=f"RFQ for {requisition.number}",
            description=requisition.justification,
            currency=requisition.currency,
        )
        for index, line in enumerate(requisition.lines.all(), start=1):
            RFQLineItem.objects.create(
                rfq=rfq,
                line_number=index,
                sku=line.sku,
                description=line.description,
                quantity=line.quantity,
                target_unit_price=line.unit_price,
            )
        conversion.rfq_id = rfq.pk
        conversion.save(update_fields=["rfq_id", "updated_at"])
    except Exception:
        conversion.notes = f"{conversion.notes}\nRFQ module unavailable; conversion recorded locally.".strip()
        conversion.save(update_fields=["notes", "updated_at"])
    transition_requisition(requisition, PurchaseRequisition.Status.CONVERTED, actor=actor, note=notes)
    return conversion


def complete_onboarding(checklist):
    if checklist.status == SupplierOnboardingChecklist.Status.COMPLETE:
        raise ValidationError("Onboarding is already complete.")
    required = ("kyb_complete", "insurance_complete", "tax_complete", "capabilities_complete")
    missing = [field for field in required if not getattr(checklist, field)]
    if missing:
        raise ValidationError(f"Cannot complete onboarding; outstanding checks: {', '.join(missing)}.")
    checklist.status = SupplierOnboardingChecklist.Status.COMPLETE
    checklist.completed_at = timezone.now()
    checklist.save(update_fields=["status", "completed_at", "updated_at"])
    supplier = checklist.supplier
    supplier.status = Supplier.Status.ACTIVE
    supplier.save(update_fields=["status", "updated_at"])
    return checklist


def start_onboarding(supplier):
    checklist, _ = SupplierOnboardingChecklist.objects.get_or_create(supplier=supplier)
    if checklist.status == SupplierOnboardingChecklist.Status.COMPLETE:
        raise ValidationError("Supplier onboarding is already complete.")
    checklist.status = SupplierOnboardingChecklist.Status.IN_PROGRESS
    checklist.save(update_fields=["status", "updated_at"])
    supplier.status = Supplier.Status.ONBOARDING
    supplier.save(update_fields=["status", "updated_at"])
    return checklist


def consume_budget(budget, amount):
    remaining = budget.allocated - budget.spent
    if amount > remaining:
        raise ValidationError("Department budget would be exceeded.")
    budget.spent += amount
    budget.save(update_fields=["spent", "updated_at"])
    return budget


def submit_sourcing_request(sourcing_request):
    return sourcing_request.submit()


def start_sourcing(sourcing_request):
    return sourcing_request.mark_in_progress()


def convert_sourcing_request(sourcing_request):
    return sourcing_request.convert()


def cancel_sourcing_request(sourcing_request):
    return sourcing_request.cancel()


def commit_budget_line(budget_line, amount):
    return budget_line.commit(amount)


def release_budget_line(budget_line, amount):
    return budget_line.release(amount)


def spend_budget_line(budget_line, amount):
    return budget_line.record_spend(amount)


def evaluate_policy(requisition):
    """Return the policy rules that apply to a requisition based on its total."""
    rules = PolicyRule.objects.filter(is_active=True).select_related("policy", "category")
    applicable = []
    for rule in rules:
        if rule.rule_type in (PolicyRule.RuleType.APPROVAL, PolicyRule.RuleType.COMMITTEE):
            if rule.threshold_amount is not None and requisition.total >= rule.threshold_amount:
                applicable.append(rule)
        elif rule.rule_type == PolicyRule.RuleType.RESTRICTION:
            if rule.category and requisition.lines.filter(
                description__icontains=rule.category.name
            ).exists():
                applicable.append(rule)
        elif rule.rule_type == PolicyRule.RuleType.QUOTE:
            applicable.append(rule)
    return applicable


def check_contract_coverage(requisition, *, contract_id, contract_number, is_covered, coverage_type="", notes="", checked_by=None):
    if requisition.status != PurchaseRequisition.Status.APPROVED:
        raise ValidationError("Contract coverage checks apply to approved requisitions only.")
    return ContractCoverageCheck.objects.create(
        requisition=requisition,
        contract_id=contract_id,
        contract_number=contract_number,
        is_covered=is_covered,
        coverage_type=coverage_type,
        notes=notes,
        checked_by=checked_by,
    )


def create_spend_category(name, code="", parent=None, description=""):
    if not name:
        raise ValidationError("A spend category name is required.")
    if SpendCategory.objects.filter(name__iexact=name).exists():
        raise ValidationError("A spend category with this name already exists.")
    return SpendCategory.objects.create(name=name, code=code, parent=parent, description=description)


def track_savings(*, title, savings_type, estimated_amount, currency="USD", category=None, requisition=None, owner=None, notes=""):
    if not title:
        raise ValidationError("A savings title is required.")
    if Decimal(str(estimated_amount)) <= 0:
        raise ValidationError("Estimated savings must be positive.")
    return SavingsTracking.objects.create(
        title=title,
        savings_type=savings_type,
        estimated_amount=estimated_amount,
        currency=currency,
        category=category,
        requisition=requisition,
        owner=owner,
        notes=notes,
    )


def realize_savings(savings, realized_amount=None):
    if realized_amount is not None:
        realized_amount = Decimal(str(realized_amount))
        if realized_amount <= 0:
            raise ValidationError("Realized amount must be positive.")
        savings.realized_amount = realized_amount
        savings.save(update_fields=["realized_amount", "updated_at"])
    return savings.realize()


def void_savings(savings):
    return savings.void()
