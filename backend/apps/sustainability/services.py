from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    CarbonFootprint,
    EsgProfile,
    EsgTarget,
    SustainabilityDeclaration,
)

PROFILE_TRANSITIONS = {
    EsgProfile.Status.DRAFT: {EsgProfile.Status.PUBLISHED, EsgProfile.Status.ARCHIVED},
    EsgProfile.Status.PUBLISHED: {EsgProfile.Status.ARCHIVED},
    EsgProfile.Status.ARCHIVED: set(),
}

DECLARATION_TRANSITIONS = {
    SustainabilityDeclaration.Status.DRAFT: {
        SustainabilityDeclaration.Status.SUBMITTED,
        SustainabilityDeclaration.Status.WITHDRAWN,
    },
    SustainabilityDeclaration.Status.SUBMITTED: {
        SustainabilityDeclaration.Status.VERIFIED,
        SustainabilityDeclaration.Status.REJECTED,
        SustainabilityDeclaration.Status.WITHDRAWN,
    },
    SustainabilityDeclaration.Status.VERIFIED: set(),
    SustainabilityDeclaration.Status.REJECTED: set(),
    SustainabilityDeclaration.Status.WITHDRAWN: set(),
}

FOOTPRINT_TRANSITIONS = {
    CarbonFootprint.Status.DRAFT: {CarbonFootprint.Status.COMPUTED},
    CarbonFootprint.Status.COMPUTED: {CarbonFootprint.Status.PUBLISHED},
    CarbonFootprint.Status.PUBLISHED: set(),
}


def publish_profile(profile, actor=None):
    if profile.status != EsgProfile.Status.DRAFT:
        raise ValidationError(f"Cannot publish a profile in status '{profile.status}'.")
    if not profile.company_name:
        raise ValidationError("A company_name is required before publishing.")
    if not profile.reporting_period_start or not profile.reporting_period_end:
        raise ValidationError("Set a reporting period before publishing the profile.")
    profile.status = EsgProfile.Status.PUBLISHED
    profile.published_at = timezone.now()
    profile.save(update_fields=["status", "published_at", "updated_at"])
    return profile


def archive_profile(profile, actor=None):
    if profile.status not in (EsgProfile.Status.DRAFT, EsgProfile.Status.PUBLISHED):
        raise ValidationError("Only draft or published profiles can be archived.")
    profile.status = EsgProfile.Status.ARCHIVED
    profile.save(update_fields=["status", "updated_at"])
    return profile


def submit_declaration(declaration, actor=None):
    if declaration.status != SustainabilityDeclaration.Status.DRAFT:
        raise ValidationError(f"Cannot submit a declaration in status '{declaration.status}'.")
    if not declaration.statement:
        raise ValidationError("A declaration statement is required before submitting.")
    declaration.status = SustainabilityDeclaration.Status.SUBMITTED
    declaration.submitted_at = timezone.now()
    declaration.save(update_fields=["status", "submitted_at", "updated_at"])
    return declaration


def verify_declaration(declaration, actor, approved, verification_notes=""):
    if declaration.status != SustainabilityDeclaration.Status.SUBMITTED:
        raise ValidationError("Only submitted declarations can be verified.")
    declaration.status = (
        SustainabilityDeclaration.Status.VERIFIED
        if approved
        else SustainabilityDeclaration.Status.REJECTED
    )
    declaration.verified_by = actor
    declaration.verified_at = timezone.now()
    declaration.verification_notes = verification_notes
    declaration.save(
        update_fields=["status", "verified_by", "verified_at", "verification_notes", "updated_at"]
    )
    return declaration


def withdraw_declaration(declaration, actor=None):
    if declaration.status not in (
        SustainabilityDeclaration.Status.DRAFT,
        SustainabilityDeclaration.Status.SUBMITTED,
    ):
        raise ValidationError("Only draft or submitted declarations can be withdrawn.")
    declaration.status = SustainabilityDeclaration.Status.WITHDRAWN
    declaration.save(update_fields=["status", "updated_at"])
    return declaration


def update_target_progress(target, current_value):
    from decimal import Decimal as D

    if current_value is None:
        raise ValidationError("A current_value is required.")
    current = D(str(current_value))
    if current < 0:
        raise ValidationError("Current value cannot be negative.")
    target.current_value = current
    baseline = target.baseline_value
    target_value = target.target_value
    if target_value < baseline:
        progress = ((current - baseline) / (target_value - baseline)) * D("100.00")
    elif target_value > baseline:
        progress = ((baseline - current) / (baseline - target_value)) * D("100.00")
    else:
        progress = D("100.00") if current >= target_value else D("0.00")
    progress = min(max(progress, D("0.00")), D("100.00")).quantize(D("0.01"))
    target.progress_percent = progress
    target.status = (
        EsgTarget.Status.ACHIEVED if progress >= D("100.00") else EsgTarget.Status.ACTIVE
    )
    target.save(update_fields=["current_value", "progress_percent", "status", "updated_at"])
    return target


@transaction.atomic
def compute_footprint_totals(footprint):
    total = Decimal("0.00")
    for record in footprint.emission_records.all():
        total += record.quantity
    footprint.total_emissions_tco2e = total.quantize(Decimal("0.01"))
    footprint.status = CarbonFootprint.Status.COMPUTED
    footprint.computed_at = timezone.now()
    footprint.save(update_fields=["total_emissions_tco2e", "status", "computed_at", "updated_at"])
    return footprint


def publish_footprint(footprint, actor=None):
    if footprint.status != CarbonFootprint.Status.COMPUTED:
        raise ValidationError("Only computed footprints can be published.")
    footprint.status = CarbonFootprint.Status.PUBLISHED
    footprint.save(update_fields=["status", "updated_at"])
    return footprint
